import os
import warnings
from pathlib import Path

import nox

from nox_utils import SUPPORTED_PYTHONS, changed_since_pypi

nox.options.stop_on_first_error = True  # Avoid premature deployment

if not (os.getenv("CI", "").lower() == "true"):
    warnings.warn("Should be in CI to run this file properly.")


@nox.session(reuse_venv=True)
def run_cli(session):
    session.install("-r", "requirements.txt")
    session.install(".")
    session.run("python", "-m", "nominally", "Bob", silent=True)
    session.run("nominally", "Bob", silent=True)
    session.run("nominally", silent=True)


@nox.session(reuse_venv=True)
@nox.parametrize("exampl", list(Path("./nominally/examples/").glob("*.py")))
def run_examples(session, exampl):
    session.install("-r", "requirements.txt")
    session.install(".")
    session.run("python", str(exampl), silent=True)


@nox.session(python=SUPPORTED_PYTHONS, reuse_venv=False)
def pytest(session):
    session.install("-r", "requirements/test.txt")
    session.install(".")
    session.run("python", "-m", "coverage", "run", "-m", "pytest")
    session.run("python", "-m", "coverage", "report")


@nox.session(reuse_venv=True)
def update_coveralls(session):
    if not os.getenv("COVERALLS_REPO_TOKEN"):
        print("No token found for Coveralls.")
        session.skip()
    session.install("-r", "requirements/test_running.txt")
    session.run("coveralls")


@nox.session(reuse_venv=True)
def deploy(session):
    session.install("-r", "requirements/deploy.txt")

    if not changed_since_pypi():
        print("PyPI is up to date.")
        session.skip()
    print("Current version is more recent than PyPI. DEPLOY!")
    session.run("python", "setup.py", "sdist", "bdist_wheel")
    session.run("python", "-m", "twine", "upload", "dist/*")
