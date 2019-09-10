import re
import subprocess
from pathlib import Path

VERSION_PATTERN = r"(\d+\.\d+\.[0-9a-z_-]+)"


def main():
    versions = {
        "git tag": get_tagged(),
        "__init__": get_module(),
        "setup.cfg": get_setup_cfg(),
    }
    the_version = set(x or "ERROR" for x in versions.values())
    if len(the_version) != 1:
        from pprint import pprint

        pprint(versions)
        raise AssertionError(f"Version problem: f{versions}")
    repo = the_version.pop()
    pypi = get_pypi()
    deployable = repo != pypi
    print(f"Current version: {repo}")
    print(f"PyPI latest:     {pypi}")
    print(f"Deployable:      {deployable}")
    return repo != pypi


def changed_since_pypi():
    return main() is True


def get_tagged():
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], stdout=subprocess.PIPE
    )
    return result.stdout.decode("utf-8").strip()


def get_module():
    path = Path("./nominally/__init__.py")
    prefix = '__version__[ ="]+?'
    return read_n_grep(path, prefix)


def get_setup_cfg():
    path = Path("./setup.cfg")
    prefix = "version[ =]+?"
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


if __name__ == "__main__":
    main()
