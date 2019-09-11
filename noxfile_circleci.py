import os
from pathlib import Path

import nox

from noxfile import SUPPORTED_PYTHONS

nox.options.stop_on_first_error = False

if not (os.getenv("CI", "").lower() == "true"):
    raise RuntimeError("Must be in CI to run this file.")


@nox.session(reuse_venv=True)
def test_run_cli(session):
    session.install("-U", "-e", ".")
    session.run("python", "-m", "nominally", "Bob", silent=True)
    session.run("nominally", "Bob", silent=True)
    session.run("nominally", silent=True)


@nox.session(reuse_venv=True)
@nox.parametrize("exampl", list(Path("./nominally/examples/").glob("*.py")))
def test_nominally_examples(session, exampl):
    session.install("-U", "-e", ".")
    session.run("python", str(exampl), silent=True)


@nox.session(python=SUPPORTED_PYTHONS, reuse_venv=False)
def test_version(session):
    session.install("-r", "requirements/test.txt")
    session.install("-e", ".")
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
    from version_check import changed_since_pypi

    if not changed_since_pypi():
        print("PyPI is up to date.")
        session.skip()
    print("Current version is more recent than PyPI. DEPLOY!")
    session.run("python", "setup.py", "sdist", "bdist_wheel")
    session.run("python", "-m", "twine", "upload", "dist/*")
