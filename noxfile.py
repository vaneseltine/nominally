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
    session.install("-r", "requirements/test.txt")
    session.install("-e", ".")
    session.run("coverage", "run", "--parallel-mode", "-m", "pytest")  # , "-rxXs")


@nox.session(reuse_venv=True)
def coverage(session):
    clean_dir("./build/coverage")
    session.install("coverage")
    if len(list(Path(".").glob(".coverage*"))) > 1:
        # Combine multiple coverage files if they exist
        try:
            Path(".coverage").unlink()
        except FileNotFoundError:
            pass
        session.run("coverage", "combine")
    session.run("coverage", "report")
    session.run("coverage", "html")


@nox.session(reuse_venv=True)
def coveralls(session):
    run_travis = os.getenv("COVERALLS_REPO_TOKEN")
    if not run_travis:  # and not Path("./.coveralls.yml").exists():
        return
    session.install("PyYAML", "coverage", "coveralls")
    session.run("coveralls")


@nox.session(reuse_venv=True)
def lint_flake8(session):
    session.install("-r", "requirements/lint.txt")
    session.run("python", "-m", "flake8", "./nominally", "--show-source")


LINT_DIRS = ["nominally", "test"]
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
@nox.parametrize("args", PYLINTS, ids=LINT_DIRS)
def lint_pylint(session, args):
    session.install("-r", "requirements/lint.txt")
    session.run("pylint", "--score=no", *args)


@nox.session(reuse_venv=True)
def lint_black(session):
    session.install("-U", "black")
    session.run("python", "-m", "black", "-t", "py36", ".")


@nox.session(reuse_venv=True)
def lint_typing(session):
    session.install("-U", "mypy")
    session.run("python", "-m", "mypy", "--strict", LINT_DIRS[0])


@nox.session(reuse_venv=True)
def lint_todos(session):
    for subpath in LINT_DIRS:
        for pyfile in (p for p in Path(subpath).glob("**/*.py") if "/_" not in str(p)):
            session.run(
                "grep",
                "-n",
                "-o",
                "#.*TODO.*$",
                "--color=auto",
                str(pyfile.absolute()),
                external=True,
                success_codes=(0, 1),
            )


if __name__ == "__main__":
    sys.stderr.write(f"Invoke {__file__} by running Nox.")
    sys.exit(1)
