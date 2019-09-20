#! /usr/bin/env python3
"""Invoke via `nox` or `python -m nox`"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import nox

nox.options.stop_on_first_error = True

PACKAGE_NAME = "nominally"
MODULE_DEFINING_VERSION = "./nominally/api.py"
VERSION_PATTERN = r"(\d+\.\d+\.[0-9a-z_-]+)"
BASIC_COMMANDS = [
    " ".join((PACKAGE_NAME, suffix))
    for suffix in ("-h", "--help", "-V", "--version", "")
]


IN_CI = os.getenv("CI", "").lower() == "true"
IN_WINDOWS = sys.platform.startswith("win")
AT_HOME = not IN_CI and not IN_WINDOWS


def supported_pythons(classifiers_in="setup.cfg"):
    """
    In Windows, return None (to just use the current interpreter)
    In other contexts, pull all supported Python classifiers from setup.cfg
    """
    if IN_WINDOWS:
        return None
    versions = []
    lines = Path(classifiers_in).read_text().splitlines()
    for line in lines:
        hit = re.match(r".*Python :: ([0-9.]+)\W*$", line)
        if hit:
            versions.append(hit.group(1))
    return versions


def pypi_needs_new_version():
    """
    Compare (and report) the version of the package:
        - as reported by package.__version__
        - as in the most recent tag
        - as on PyPI right now
    Raise concern about __version__ / git tag mismatch.
    Treat any *dev* version as not PyPI-able.
    Print out the versions.
    Return true if the current version is consistent, non-dev, ahead of PyPI.
    """
    versions = {
        "__version__": get_package_version(MODULE_DEFINING_VERSION),
        "docs": get_docs_version(),
        "git tag": get_tagged_version(),
    }
    the_version = {x or "ERROR" for x in versions.values()}
    if len(the_version) != 1:
        from pprint import pprint

        print(f"Version inconsistency!")
        pprint(versions, width=10)
        return False
    repo_v = the_version.pop()
    pypi_v = get_pypi_version()
    deployable = (repo_v != pypi_v) and "dev" not in repo_v
    print(f"Internal:      {versions['__version__']}")
    print(f"Documentation: {versions['docs']}")
    print(f"Git tag:       {versions['git tag']}")
    print(f"PyPI:          {pypi_v}")
    print(f"Deployable:    {deployable}")
    return deployable


def get_tagged_version():
    """Return the latest git tag"""
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], stdout=subprocess.PIPE
    )
    return result.stdout.decode("utf-8").strip()


def get_package_version(defined_in):
    """Return the defined ___version__ by scraping from given module."""
    path = Path(defined_in)
    pattern = '__version__[ ="]+?' + VERSION_PATTERN
    return search_in_file(path, pattern)


def get_docs_version():
    from docs import conf

    return conf.release


def search_in_file(path, pattern, encoding="utf-8"):
    text = Path(path).read_text(encoding)
    result = re.compile(pattern).search(text)
    if not result:
        return None
    return result.group(1)


def get_pypi_version(encoding="utf-8"):
    """Scrape the latest version of this package on PyPI"""
    result = subprocess.check_output(
        ["python", "-m", "pip", "search", PACKAGE_NAME]
    ).decode(encoding)
    complete_pattern = "^" + PACKAGE_NAME + r" \(" + VERSION_PATTERN
    matched = re.search(complete_pattern, result)
    try:
        return matched.group(1)
    except AttributeError:
        return None


@nox.session(python=False)
def lint_flake8(session):
    session.run("flake8", ".")


@nox.session(python=False)
def lint_pylint(session):
    for args in [PACKAGE_NAME, "test --rcfile=./test/pylintrc"]:
        cmd = "python -m pylint --score=no"
        session.run(*cmd.split(), *args.split())


@nox.session(python=False)
def lint_typing(session, subfolder=PACKAGE_NAME):
    session.run("python", "-m", "mypy", "--strict", PACKAGE_NAME)


@nox.session(python=False)
def lint_black(session):
    session.run("python", "-m", "black", "-t", "py36", ".")


@nox.session(python=False)
def lint_todos(session):
    for file in Path(".").glob("*/*.py"):
        result = search_in_file(file, "((TODO|FIXME).*)")
        if result:
            print(file, result)


@nox.session(python=supported_pythons(), reuse_venv=False)
def pytest(session):
    session.install("-r", "requirements/test.txt")
    session.install("-e", ".")
    session.run("python", "-m", "coverage", "run", "-m", "pytest")
    session.run("python", "-m", "coverage", "report")
    run_various_invocations(session, cmds=BASIC_COMMANDS)


def run_various_invocations(session, cmds):
    for prefix in ["", "python -m "]:
        for core_cmd in cmds:
            complete_cmd = (prefix + core_cmd).split()
            session.run(*complete_cmd, silent=True)


@nox.session(python=False)
def coverage(session):
    if IN_CI:
        session.run("coveralls")
        return
    session.run("python", "-m", "coverage", "html")
    output = Path("build/coverage/index.html").resolve()
    print(f"Coverage at {output}")


@nox.session(python=False)
def lint_docs(session):
    session.run("doc8", "docs", "-q")


@nox.session(python=False)
def build_docs(session):
    if IN_CI:
        session.skip("Not building on CI")
    output_dir = Path("build/docs").resolve()
    shutil.rmtree(output_dir, ignore_errors=True)  # eradicate previous build
    session.run(
        "python",
        "-m",
        "sphinx",
        "docs",
        str(output_dir),
        "-q",  # only output problems
        "-a",  # don't reuse old output
        "-E",  # don't reuse previous environment
        "-n",  # nitpicky mode
        "-W",  # warnings are errors
        "--keep-going",  # gather all warnings before exit
    )
    print(f"Documentation at {output_dir / 'index.html'}")


@nox.session(python=False)
def deploy_to_pypi(session):
    if not pypi_needs_new_version():
        session.skip("PyPI already up to date")
    print("Current version is ready to deploy to PyPI.")
    if not IN_CI:
        session.skip("Only deploying from CI")
    session.run("python", "setup.py", "sdist", "bdist_wheel")
    session.run("python", "-m", "twine", "upload", "dist/*")


@nox.session(python=False)
def autopush_repo(session):
    if not nox.options.stop_on_first_error:
        session.skip("Error-free runs required")
    git_output = subprocess.check_output(["git", "status", "--porcelain"])
    if git_output:
        print(git_output.decode("ascii").rstrip())
        session.skip("Local repo is not clean")
    if not AT_HOME:
        session.skip("Only from home")
    subprocess.check_output(["git", "push"])


if __name__ == "__main__":
    print(f"Pythons supported: {supported_pythons()}")
    pypi_needs_new_version()
    print(f"Invoke {__file__} by running Nox.")
