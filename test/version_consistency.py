import re
import subprocess
from pathlib import Path

VERSION_PATTERN = r"(\d+\.\d+\.\d+)"


def main():
    versions = {
        "git tag": get_tagged(),
        "__init__": get_module(),
        "setup.cfg": get_setup_cfg(),
    }
    if len(set(versions.values())) != 1:
        from pprint import pprint

        pprint(versions)
        raise AssertionError(f"Version problem: f{versions}")


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


if __name__ == "__main__":
    main()
