#! /usr/bin/env python3
"""Invoke via `nox` or `python -m nox`"""

import os
import re
import subprocess
import sys
from pathlib import Path
from shutil import rmtree

import nox

CI_LIVE = os.getenv("CI", "").lower() == "true"
if CI_LIVE:
    nox.options.stop_on_first_error = True  # Avoid premature deployment

VERSION_PATTERN = r"(\d+\.\d+\.[0-9a-z_-]+)"


def changed_since_pypi():
    versions = {"__version__": get_module(), "git tag": get_tagged()}
    the_version = {x or "ERROR" for x in versions.values()}
    if len(the_version) != 1:
        from pprint import pprint

        print(f"Version inconsistency!")
        pprint(versions, width=10)
        return False
    repo_v = the_version.pop()
    pypi_v = get_pypi()
    deployable = (repo_v != pypi_v) and "dev" not in repo_v
    print(f"Local:         {versions['__version__']}")
    print(f"Git tag:       {versions['git tag']}")
    print(f"PyPI:          {pypi_v}")
    print(f"Deployable:    {deployable}")
    return deployable


def get_tagged():
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], stdout=subprocess.PIPE
    )
    return result.stdout.decode("utf-8").strip()


def get_module():
    path = Path("./nominally/__init__.py")
    prefix = '__version__[ ="]+?'
    return read_n_grep(path, prefix)


def read_n_grep(path, prefix, pattern=VERSION_PATTERN):
    text = Path(path).read_text()
    result = re.compile(prefix + pattern).search(text)
    if not result:
        return f"Failed to find version in {path}"
    return result.group(1)


def get_pypi():
    result = subprocess.check_output(
        ["python", "-m", "pip", "search", "nominally"]
    ).decode("utf-8")
    matc = re.compile(r"^nominally \(" + VERSION_PATTERN).search(result)
    return matc.group(1)


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
def lint_flake8(session):
    session.install("-r", "requirements/lint.txt")
    for lint_dir in ["nominally", "test", "."]:
        cmd = f"python -m flake8 --show-source {lint_dir}/*.py".split()
        session.run(*cmd)


@nox.session(reuse_venv=True)
def lint_pylint(session):
    session.install("-r", "requirements/lint.txt")
    for args in [
        "nominally",
        "test -d invalid-name -d no-self-use -d protected-access -d too-few-public-methods",
        "*.py",
    ]:
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


@nox.session(reuse_venv=True)
def lint_todos(session):
    for lint_dir in ["nominally", "test"]:
        cmd = f"grep -ire 'TODO.*' -n -o --color=auto {lint_dir}".split()
        session.run(*cmd, external=True, success_codes=[0, 1])


@nox.session(reuse_venv=False)
def run_clis(session):
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
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
def run_examples(session):
    examples = list(Path("./nominally/examples/").glob("*.py"))
    session.install("-r", "requirements.txt")
    session.install(".")
    for example in examples:
        session.run("python", str(example), silent=True)


@nox.session(python=SUPPORTED_PYTHONS, reuse_venv=False)
def pytest(session):
    session.install("-r", "requirements/test.txt")
    session.install(".")
    session.run("python", "-m", "coverage", "run", "-m", "pytest")
    session.run("python", "-m", "coverage", "report")


@nox.session(reuse_venv=True)
def coverage(session):
    session.install("-r", "requirements/test.txt")
    if CI_LIVE:
        session.install("-r", "requirements/test_running.txt")
        session.run("coveralls")
        return
    make_clean_dir("./build/coverage")
    session.run("python", "-m", "coverage", "html")


@nox.session(reuse_venv=True)
def deploy(session):
    if not changed_since_pypi():
        session.skip("PyPI is up to date.")
    if not CI_LIVE:
        session.skip("Deploy only from CI.")
    print("Current version is more recent than PyPI. DEPLOY!")
    session.install("-r", "requirements/deploy.txt")
    session.run("python", "setup.py", "sdist", "bdist_wheel")
    session.run("python", "-m", "twine", "upload", "dist/*")


if __name__ == "__main__":
    print(f"Pythons supported: {SUPPORTED_PYTHONS}")
    changed_since_pypi()
    sys.stderr.write(f"Invoke {__file__} by running Nox.")
    sys.exit(1)
