"""Invoke via `nox` or `python -m nox`"""

import re
import sys
from pathlib import Path
from shutil import rmtree

import nox

nox.options.reuse_existing_virtualenvs = False
nox.options.stop_on_first_error = False

CORE_PYTHON = "3.6"
LINT_DIRS = ["nominally", "test"]
print(LINT_DIRS)
PYLINT_ARGS = [
    "nominally",
    "test -d invalid-name -d no-self-use -d protected-access -d too-few-public-methods",
]
EXAMPLES = list(Path("./nominally/examples/").glob("*.py"))


def get_versions_from_classifiers(deploy_file):
    versions = []
    lines = Path(deploy_file).read_text().splitlines()
    for line in lines:
        hit = re.match(r".*Python :: ([0-9.]+)\W*$", line)
        if hit:
            versions.append(hit.group(1))
    return versions


SUPPORTED_PYTHONS = get_versions_from_classifiers("setup.cfg")


def make_clean_dir(s):
    folder = Path(s)
    if folder.exists():
        rmtree(folder, ignore_errors=True)
    else:
        folder.parent.mkdir(exist_ok=True)


@nox.session(reuse_venv=True)
@nox.parametrize("lint_dir", LINT_DIRS.copy())
def lint_flake8(session, lint_dir):
    session.install("-r", "requirements/lint.txt")
    cmd = f"python -m flake8 --show-source {lint_dir}/*.py".split()
    session.run(*cmd)


@nox.session(reuse_venv=True)
@nox.parametrize("args", PYLINT_ARGS)
def lint_pylint(session, args):
    session.install("-r", "requirements/lint.txt")
    cmd = "python -m pylint --score=no".split() + args.split()
    session.run(*cmd)


@nox.session(reuse_venv=True)
def lint_typing(session):
    session.install("-U", "mypy")
    session.install("-r", "requirements.txt")
    cmd = "python -m mypy --strict nominally".split()
    session.run(*cmd)


@nox.session(reuse_venv=True)
def lint_black(session):
    session.install("-U", "black")
    cmd = "python -m black -t py36 --check .".split()
    session.run(*cmd)


@nox.session(reuse_venv=False)
def run_clis(session):
    """
    Not parameterized because it's not really worth polluting the report.
    """
    session.install("-U", "-e", ".")
    for prefix in ["", "python -m "]:
        for main_cmd in [
            "nominally Bob",
            "nominally -h",
            "nominally --help",
            "nominally -V",
            "nominally --version",
        ]:
            cmd = (prefix + main_cmd).split()
            session.run(*cmd, silent=True)


@nox.session(reuse_venv=False)
@nox.parametrize("example", EXAMPLES)
def run_examples(session, example):
    session.install("-r", "requirements.txt")
    session.install(".")
    session.run("python", str(example), silent=True)


@nox.session(python=SUPPORTED_PYTHONS, reuse_venv=False)
def pytest(session):
    session.install("-r", "requirements/test.txt")
    session.install(".")
    cov_subcmd = "coverage run -m " if session.python == CORE_PYTHON else ""
    cmd = f"python -m {cov_subcmd}pytest".split()
    session.run(*cmd)


@nox.session(python=f"python{CORE_PYTHON}", reuse_venv=True)
def coverage(session):
    session.install("-r", "requirements/test.txt")
    session.run("python", "-m", "coverage", "report")
    make_clean_dir("./build/coverage")
    session.run("python", "-m", "coverage", "html")


@nox.session(reuse_venv=True)
def find_todos(session):
    for lint_dir in LINT_DIRS:
        path = str(Path(lint_dir).absolute())
        cmd = f"grep -ire 'TODO.*' -n -o --color=auto {path}".split()
        session.run(*cmd, external=True, success_codes=[0, 1])


if __name__ == "__main__":
    print(f"Pythons supported: {SUPPORTED_PYTHONS}")
    sys.stderr.write(f"Invoke {__file__} by running Nox.")
    sys.exit(1)
