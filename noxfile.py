#! /usr/bin/env python3
"""Invoke via `nox` or `python -m nox`"""

import os
import subprocess
import sys
import webbrowser
from pathlib import Path

import nox

from noxhelpers import SUPPORTED_PYTHONS, pypi_is_outdated, read_n_grep

IN_CI = os.getenv("CI", "").lower() == "true"
IN_WINDOWS = sys.platform.startswith("win")
AT_HOME = not IN_CI and not IN_WINDOWS

nox.options.stop_on_first_error = True


@nox.session(python=False)
def lint_flake8(session):
    cmd = f"flake8 .".split()
    session.run(*cmd)


@nox.session(python=False)
def lint_pylint(session):
    for args in ["nominally", "test --rcfile=./test/pylintrc"]:
        cmd = (" ".join(("python -m pylint --score=no", args))).split()
        session.run(*cmd)


@nox.session(python=False)
def lint_typing(session):
    cmd = "python -m mypy --strict nominally".split()
    session.run(*cmd)


@nox.session(python=False)
def lint_black(session):
    cmd = "python -m black -t py36 .".split()
    if IN_CI:
        cmd = cmd + ["--check"]
    session.run(*cmd)


@nox.session(python=False)
def lint_todos(session):
    for file in Path(".").glob("*/*.py"):
        result = read_n_grep(file, "((TODO|FIXME).*)")
        if result:
            print(file, result)


@nox.session(python=SUPPORTED_PYTHONS, reuse_venv=False)
def pytest(session):
    session.install("-r", "requirements/test.txt")
    session.install(".")
    session.run("python", "-m", "coverage", "run", "-m", "pytest")
    session.run("python", "-m", "coverage", "report")
    run_various_invocations(session)


def run_various_invocations(session):

    core_commands = [
        "nominally -h",
        "nominally --help",
        "nominally -V",
        "nominally --version",
        "nominally Vimes",
    ]

    for prefix in ["", "python -m "]:
        for main_cmd in core_commands:
            cmd = (prefix + main_cmd).split()
            session.run(*cmd, silent=True)


@nox.session(python=False)
def coverage(session):
    if IN_CI:
        session.run("coveralls")
        return
    session.run("python", "-m", "coverage", "html")


@nox.session(python=False)
def lint_docs(session):
    session.run("doc8", "docs", "-q")


@nox.session(python=False)
def build_docs(session):
    if IN_CI:
        session.skip("Not building on CI")
    sphinx_options = "-q -a -E -n -W".split()
    output_dir = "build/docs"
    session.run("python", "-m", "sphinx", "docs", "build/docs", *sphinx_options)
    index = Path(output_dir).resolve() / "index.html"
    webbrowser.open_new_tab(f"file://{index}")


@nox.session(python=False)
def deploy_to_pypi(session):
    if not pypi_is_outdated():
        session.skip("PyPI up to date")
    if not IN_CI:
        session.skip("Deploy only from CI")
    print("Current version is more recent than PyPI. DEPLOY!")
    session.run("python", "setup.py", "sdist", "bdist_wheel")
    session.run("python", "-m", "twine", "upload", "dist/*")


@nox.session(python=False)
def push_to_github(session):
    if not nox.options.stop_on_first_error:
        session.skip("Error-free run disabled")
    if not AT_HOME:
        session.skip("Auto-push only from home")
    git_output = subprocess.check_output(["git", "status", "--porcelain"])
    if git_output:
        print(git_output.decode("ascii").rstrip())
        session.skip("Local repo is not clean")
    output = subprocess.check_output(["git", "push"])
    print(output.decode("utf8"))


if __name__ == "__main__":
    print(f"Pythons supported: {SUPPORTED_PYTHONS}")
    pypi_is_outdated()
    print(f"Invoke {__file__} by running Nox.")
