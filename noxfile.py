"""Nox

cf. https://github.com/saltstack/salt/blob
    /328989d6cc8f81fc100c9aa900a4e3613dc7c19d/noxfile.py

For .env setup, see .circleci/env"""

import os
import sys
from pathlib import Path
from shutil import rmtree

import dotenv
import nox

# -r on CLI to override and reuse all instead
nox.options.reuse_existing_virtualenvs = False
# --no-stop-on-first-error on CLI to override
nox.options.stop_on_first_error = True

SUPPORTED_PYTHONS = ("python3.6", "python3.7")  # , "python3.8") - numpy
DISTROS = ["mssql", "mysql", "postgresql", "sqlite"]
WINDOWS = sys.platform.startswith("win")

# Pull variables, especially LFTEST_*, into os.environ
dotenv.load_dotenv(dotenv.find_dotenv())


def get_machine_distros(distros):
    supported = [d for d in distros if os.environ.get(f"LFTEST_{d.upper()}") == "1"]
    return supported or ["sqlite"]


def clean_dir(s):
    folder = Path(s)
    if folder.exists():
        rmtree(folder, ignore_errors=True)


@nox.session(reuse_venv=False)
@nox.parametrize("distro", get_machine_distros(DISTROS))
def test_database(session, distro):
    session.install("-r", "requirements.txt")
    session.install("-e", f".[{distro},excel]")
    session.run(
        "coverage",
        "run",
        "--parallel-mode",
        "-m",
        "pytest",
        "-rxXs",
        f"test/distro_specific/{distro}.py",
        env={"LFTEST_DISTRO": distro},
    )
    session.run(
        "coverage",
        "run",
        "--parallel-mode",
        "-m",
        "pytest",
        "-rxXs",
        env={"LFTEST_DISTRO": distro},
    )


@nox.session(python=SUPPORTED_PYTHONS, reuse_venv=False)
def test_version(session):
    session.install("-r", "requirements.txt")
    session.install("-e", ".[excel]")
    session.run(
        "coverage",
        "run",
        "--parallel-mode",
        "-m",
        "pytest",
        "-rxXs",
        env={
            "LFTEST_DISTRO": "sqlite",
            "LFTEST_SQLITE": "1",
            "LFTEST_SQLITE_DATABASE": ":memory:",
        },
    )


@nox.session(python=SUPPORTED_PYTHONS, reuse_venv=False)
def cli(session):
    session.install("-e", ".")
    session.chdir("/")
    session.run("python", "-m", "laforge", "--version", silent=True)
    session.run("laforge", "--version", silent=True)
    session.run("laforge", "env", "--no-warning", silent=True)
    session.run("laforge", "consult", "--match", "diagnostic", silent=True)


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
def docs_doc8(session):
    session.install("-U", "doc8", "Pygments")
    if WINDOWS:
        session.run("doc8", "./docs", "-q", "--ignore=D002", "--ignore=D004")
    else:
        session.run("doc8", "./docs", "-q")


@nox.session(reuse_venv=True)
def docs_sphinx(session):
    # Treat warnings as errors.
    session.env["SPHINXOPTS"] = "-W"
    session.install("-e", ".")
    session.install("-r", "./docs/requirements.txt")
    clean_dir("./build/sphinx")
    session.run("python", "-m", "sphinx", "-b", "coverage", "./docs", "./docs/_static")
    session.run("python", "setup.py", "build_sphinx", "-b", "html", "-W")


@nox.session(reuse_venv=True)
def lint_flake8(session):
    session.install("-U", "flake8")
    session.run("python", "-m", "flake8", "./laforge", "--show-source")


@nox.session(reuse_venv=True)
def lint_pylint(session):
    session.install("-U", "pylint")
    session.run("pylint", "./laforge", "-d", "import-error")


@nox.session(reuse_venv=True)
def lint_black(session):
    session.install("-U", "black")
    session.run("python", "-m", "black", "--target-version", "py36", ".")


if __name__ == "__main__":
    sys.stderr.write(f"Invoke {__file__} by running Nox.")
    sys.exit(1)
