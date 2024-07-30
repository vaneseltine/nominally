import json
import typing as T
from pathlib import Path

import pytest

TEST_DATA_DIRECTORY = Path(__file__).parent / "names"


def dict_entry_test(testclass: T.Callable, entry: T.Mapping[str, str], **kwargs):
    """
    Simplified test interface for asserting a dictionary containing raw input and
    expected results.

    Arguments:
    - testclass is the class under test (typically Name)
    - entry is a dict containing a "raw" key and at least one other key to retrieve.
    - **kwargs are passed on to testclass

    Example:

    dict_entry_test(
        Name,
        {"raw": "vimes, samuel x", "first": "samuel", "middle": "x", "last": "vimes"},
    )
    This ensures that dict(Class(raw)) produces the output name parts:
    - dict(Class(raw))["first"] == "samuel"
    - dict(Class(raw))["middle"] == "x"
    - dict(Class(raw))["last"] == "vimes"
    """
    observed = dict(testclass(entry["raw"], **kwargs))
    expected = {key: entry.get(key, "") for key in observed.keys()}
    expected["suffix"] = set(expected["suffix"].split())  # type: ignore
    observed["suffix"] = set(observed["suffix"].split())
    assert observed == expected


def load_bank(glob):
    test_bank_files = list(TEST_DATA_DIRECTORY.glob(f"{glob}.json"))
    total_bank = []
    for path in test_bank_files:
        test_bank = json.loads(path.read_text(encoding="utf8"))
        total_bank.extend(test_bank)
    return total_bank


def make_ids(entry):
    return entry.get("id") or entry.get("raw")


@pytest.fixture(autouse=True)
def add_output_spacing():
    print("")
    yield
    print("")
