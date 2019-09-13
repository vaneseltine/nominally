import json
from pathlib import Path

import pytest

TEST_DATA_DIRECTORY = Path(__file__).parent / "names"


def dict_entry_test(testclass, entry):
    n = testclass(entry["raw"])
    observed = dict(n)
    expected = {key: entry.get(key, "") for key in observed.keys()}
    expected["suffix"] = set(expected["suffix"])
    observed["suffix"] = set(observed["suffix"])
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


@pytest.fixture(autouse=False)
def add_output_spacing():
    print("")
    yield
    print("")
