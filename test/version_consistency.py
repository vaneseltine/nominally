import re
import subprocess
from pathlib import Path

VERSION_PATTERN = re.compile(r"version.*?(\d+\.\d+\.\d+)")


def get_tagged():
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], stdout=subprocess.PIPE
    )
    return result.stdout.decode("utf-8").strip()


def read_n_grep(path, pattern):
    text = path.read_text()
    return pattern.search(text).group(1)


def get_module():
    return read_n_grep(Path("./nominally/__init__.py"), VERSION_PATTERN)


def get_setup_cfg():
    return read_n_grep(Path("./setup.cfg"), VERSION_PATTERN)


def main():
    versions = {
        "git tag": get_tagged(),
        "__init__": get_module(),
        "setup.cfg": get_setup_cfg(),
    }
    if len(set(versions.values())) != 1:
        raise AssertionError(f"Inconsistent versions: f{versions}")


if __name__ == "__main__":
    main()
