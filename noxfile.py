#! /usr/bin/env python3
"""Invoke via `nox` or `python -m nox`"""

import json
import os
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

import nox

nox.options.stop_on_first_error = True
nox.options.keywords = "test or lint"

PACKAGE_NAME = "nominally"
MODULE_DEFINING_VERSION = "./nominally/api.py"
VERSION_PATTERN = r"(\d+\.\d+\.[0-9a-z_-]+)"
BASIC_COMMANDS = [
    " ".join((PACKAGE_NAME, suffix))
    for suffix in (
        "-h",
        "--help",
        "-V",
        "--version",
        "",
        '''"Mr. Arthur 'Two Sheds' Jackson"''',
    )
]


IN_CI = os.getenv("CI", "").lower() == "true"


def supported_pythons(classifiers_file=Path("pyproject.toml")):
    """
    Parse all supported Python classifiers from pyproject.toml
    """
    pattern = re.compile(r"Programming Language :: Python :: ([0-9]+\.[0-9.]+)")
    return pattern.findall(classifiers_file.read_text(encoding="utf-8"))


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
        "Internal module": get_package_version(MODULE_DEFINING_VERSION),
        "pyproject.toml": get_pyproject_version(),
        "Git tag": get_tagged_version(),
    }
    if not IN_CI:
        versions["Documentation"] = get_docs_version()

    the_version = {x or "ERROR" for x in versions.values()}
    broken = len(the_version) > 1

    versions["PyPI"] = get_pypi_version()
    if broken:
        print("\nVersion inconsistency!\n")
        deployable = False
    else:
        repo_v = the_version.pop()
        deployable = (repo_v != versions["PyPI"]) and "dev" not in repo_v

    versions["Deployable"] = deployable
    for k, v in versions.items():
        print(f"{k:<15}: {v}")
    return deployable


def get_pyproject_version():
    return search_in_file("pyproject.toml", 'version = "' + VERSION_PATTERN)


def get_tagged_version():
    """Return the latest git tag"""
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], check=True, stdout=subprocess.PIPE
    )
    return result.stdout.decode("utf-8").strip()


def get_package_version(defined_in):
    """Return the defined ___version__ by scraping from given module."""
    path = Path(defined_in)
    pattern = '__version__[ ="]+?' + VERSION_PATTERN
    return search_in_file(path, pattern)


def get_docs_version():
    from docs import conf  # pylint:disable=import-outside-toplevel

    return conf.release


def search_in_file(path, pattern, encoding="utf-8"):
    text = Path(path).read_text(encoding)
    result = re.compile(pattern).search(text)
    if not result:
        return None
    return result.group(1)


def get_pypi_version(encoding="utf-8"):
    """Scrape the latest version of this package on PyPI"""

    pypi_body = urllib.request.urlopen("https://pypi.org/pypi/nominally/json").read()
    pypi_json = json.loads(pypi_body.decode(encoding))

    return pypi_json["info"]["version"]


@nox.session(python=False)
def lint_black(session):
    session.run("python", "-m", "black", "-t", "py37", ".")


@nox.session(python=False)
def lint_ruff(session, subfolder=PACKAGE_NAME):
    session.run("python", "-m", "ruff", "check", subfolder)


@nox.session(python=False)
def lint_pylint(session):
    for args in [PACKAGE_NAME, "test --rcfile=./test/pylintrc"]:
        cmd = "python -m pylint --score=no"
        session.run(*cmd.split(), *args.split())


@nox.session(python=False)
def lint_typing(session, subfolder=PACKAGE_NAME):
    session.run("python", "-m", "mypy", "--strict", subfolder)


@nox.session(python=False)
def lint_todos(_):
    for file in Path(".").glob("*/*.py"):
        result = search_in_file(file, "((TODO|FIXME).*)")
        if result:
            print(file, result)


@nox.session(python=supported_pythons(), reuse_venv=False)
def test_pytest(session):
    session.install("-r", "requirements/test.txt")
    session.install("-e", ".")
    cmd = ["python", "-m", "coverage", "run", "-m", "pytest"]
    if IN_CI:
        cmd.append("--junit-xml=build/pytest/results.xml")
    session.run(*cmd)


@nox.session(python=supported_pythons(), reuse_venv=True)
def test_cli_does_not_crash(session, cmds=BASIC_COMMANDS):
    session.install("-e", ".")
    for prefix in ["", "python -m "]:
        for core_cmd in cmds:
            complete_cmd = (prefix + core_cmd).split()
            session.run(*complete_cmd, silent=True)


@nox.session(python=False)
def test_coverage(session):
    session.run("python", "-m", "coverage", "html")
    output = Path("build/coverage/index.html").resolve()
    session.run("python", "-m", "coverage", "report")
    print(f"Coverage at {output}")


@nox.session(python=["3.12"], reuse_venv=True)
def build_docs(session):
    session.run("doc8", "docs", "-q")
    session.install("-r", "requirements/docs.txt")
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
def autopush_repo(session):
    if IN_CI:
        session.skip("Not pushing on CI")
    if not nox.options.stop_on_first_error:
        session.skip("Error-free runs required")
    git_output = subprocess.check_output(["git", "status", "--porcelain"])
    if git_output:
        print(git_output.decode("ascii").rstrip())
        session.skip("Local repo is not clean")
    subprocess.check_output(["git", "push"])


if __name__ == "__main__":
    print(f"Pythons supported: {supported_pythons()}")
    pypi_needs_new_version()
    print(f"Invoke {__file__} by running Nox.")
