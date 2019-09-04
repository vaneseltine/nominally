"""Invoke via `nox` or `python -m nox`"""

import os
import sys
from pathlib import Path
from shutil import rmtree

import nox

# -r on CLI to override and reuse all instead
nox.options.reuse_existing_virtualenvs = False
# --no-stop-on-first-error on CLI to override
nox.options.stop_on_first_error = False

SUPPORTED_PYTHONS = ("python3.6", "python3.7", "python3.8")


def clean_dir(s):
    folder = Path(s)
    if folder.exists():
        rmtree(folder, ignore_errors=True)


@nox.session(python=SUPPORTED_PYTHONS, reuse_venv=False)
def test_version(session):
    session.install("-r", "requirements.txt")
    session.install("-e", ".")
    session.run("coverage", "run", "--parallel-mode", "-m", "pytest", "-rxXs")


@nox.session(reuse_venv=True)
def coverage(session):
    clean_dir("./build/coverage")
    session.install("coverage")
    if len(list(Path(".").glob(".coverage*"))) > 1:
        try:
            Path(".coverage").unlink()
        except FileNotFoundError:
            pass
        session.run("coverage", "combine")
    session.run("coverage", "report")
    session.run("coverage", "html")


@nox.session(reuse_venv=True)
def coveralls(session):
    if os.getenv("COVERALLS_REPO_TOKEN"):
        session.install("coverage", "coveralls")
        session.run("coveralls")


@nox.session(reuse_venv=True)
def lint_flake8(session):
    session.install("-U", "flake8")
    session.run("python", "-m", "flake8", "./nominally", "--show-source")


@nox.session(reuse_venv=True)
def lint_pylint(session):
    session.install("-U", "pylint")
    session.run("pylint", "./nominally", "-d", "import-error")


@nox.session(reuse_venv=True)
def lint_black(session):
    session.install("-U", "black")
    session.run("python", "-m", "black", "-t", "py36", ".")


if __name__ == "__main__":
    sys.stderr.write(f"Invoke {__file__} by running Nox.")
    sys.exit(1)
