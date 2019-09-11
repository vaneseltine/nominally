"""Invoke via `nox` or `python -m nox`"""

import os
import sys
from pathlib import Path
from shutil import rmtree

import nox

# -r on CLI to override and reuse all instead
nox.options.reuse_existing_virtualenvs = False
# --no-stop-on-first-error on CLI to override
nox.options.stop_on_first_error = True

CI = os.getenv("CIRCLECI", "").lower() == "true"


LINT_DIRS = ["nominally", "test"]


def make_clean_dir(s):
    folder = Path(s)
    if folder.exists():
        rmtree(folder, ignore_errors=True)
    else:
        folder.parent.mkdir(exist_ok=True)


@nox.session(reuse_venv=True)
@nox.parametrize("path", LINT_DIRS.copy())
def lint_flake8(session, path):
    session.install("-r", "requirements/lint.txt")
    session.run("python", "-m", "flake8", str(path), "--show-source")


PYLINTS = [
    ["nominally"],
    [
        "test",
        "-d",
        "invalid-name",
        "-d",
        "no-self-use",
        "-d",
        "protected-access",
        "-d",
        "too-few-public-methods",
        "-d",
        "unused-import",
    ],
]


@nox.session(reuse_venv=True)
@nox.parametrize("args", PYLINTS, ids=LINT_DIRS.copy())
def lint_pylint(session, args):
    session.install("-r", "requirements/lint.txt")
    session.run("python", "-m", "pylint", "--score=no", *args)


@nox.session(reuse_venv=True)
def lint_typing(session):
    session.install("-U", "mypy")
    session.run("python", "-m", "mypy", "--strict", LINT_DIRS[0])


@nox.session(reuse_venv=True)
def lint_black(session):
    session.install("-U", "black")
    session.run(*"python -m black -t py36 --check .".split(), silent=True)


@nox.session(reuse_venv=True)
def test_run_cli(session):
    session.install("-U", "-e", ".")
    session.run("python", "-m", "nominally", "Bob", silent=True)
    session.run("nominally", "Bob", silent=True)
    session.run("nominally", silent=True)


@nox.session(reuse_venv=True)
@nox.parametrize("example", list(Path("./nominally/examples/").glob("*.py")))
def test_run_examples(session, example):
    session.install("-U", "-e", ".")
    session.run("python", str(example), silent=True)


@nox.session(python=("python3.6", "python3.7", "python3.8"), reuse_venv=False)
def test_version(session):
    session.install("-r", "requirements/test.txt")
    session.install("-e", ".")
    session.run("python", "-m", "coverage", "run", "-m", "pytest")


@nox.session(reuse_venv=True)
def test_coverage(session):
    make_clean_dir("./build/coverage")
    session.install("coverage==4.5.3")
    if len(list(Path(".").glob(".coverage*"))) > 1:
        print("Combining multiple coverage files...")
        try:
            Path(".coverage").unlink()
        except FileNotFoundError:
            pass
        session.run("python", "-m", "coverage", "combine")
    session.run("python", "-m", "coverage", "report")
    session.run("python", "-m", "coverage", "html")


@nox.session(reuse_venv=True)
def todos(session):
    TODO_GREPPER = r"TODO.*"
    for subpath in LINT_DIRS:
        session.run(
            "grep",
            "-ire",
            TODO_GREPPER,
            "-n",
            "-o",
            "--color=auto",
            str(Path(subpath).absolute()),
            external=True,
            success_codes=(0, 1),
        )


if __name__ == "__main__":
    sys.stderr.write(f"Invoke {__file__} by running Nox.")
    sys.exit(1)
