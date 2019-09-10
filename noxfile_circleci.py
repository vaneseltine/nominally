import os
from pathlib import Path
from shutil import rmtree

import nox

nox.options.stop_on_first_error = False

if not (os.getenv("CI", "").lower() == "true"):
    raise RuntimeError("Must be in CI to run this file.")


def make_clean_dir(s):
    folder = Path(s)
    if folder.exists():
        rmtree(folder, ignore_errors=True)
    else:
        folder.parent.mkdir(exist_ok=True)


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


@nox.session(python=("python3.6", "python3.7", "python3.8"), reuse_venv=False)
def test_version(session):
    session.install("-r", "requirements/test.txt")
    session.install("-e", ".")
    session.run("coverage", "run", "-m", "pytest")


@nox.session(reuse_venv=True)
def coverage(session):
    make_clean_dir("./build/coverage")
    session.install("coverage")
    if len(list(Path(".").glob(".coverage*"))) > 1:
        print("Combining multiple coverage files...")
        try:
            Path(".coverage").unlink()
        except FileNotFoundError:
            pass
        session.run("coverage", "combine")
    session.run("coverage", "report")


@nox.session(reuse_venv=True)
def coverage_coveralls(session):
    coveralls_live = os.getenv("COVERALLS_REPO_TOKEN")
    if not coveralls_live:
        session.run("coverage", "html")
        return
    session.install("PyYAML", "coverage", "coveralls")
    session.run("coveralls")


@nox.session(reuse_venv=True)
def deploy(session):
    session.install("-r", "requirements/deploy.txt")
    from version_check import changed_since_pypi

    if not changed_since_pypi():
        print("PyPI is up to date.")
        session.skip()
    print("Current version is more recent than PyPI.")
    make_clean_dir("./dist")
    session.run("python", "setup.py", "sdist", "bdist_wheel")
    session.run("twine", "upload", "dist/*")
