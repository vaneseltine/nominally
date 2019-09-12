import json
from pathlib import Path

import pytest

from nominally.parser import logger

TEST_DATA_DIRECTORY = Path(__file__).parent / "names"


def dict_entry_test(testclass, entry):
    n = testclass(entry["raw"])
    expected = {key: entry.get(key, "") for key in dict(n).keys()}
    assert dict(n) == expected


def load_bank(glob):
    test_bank_files = list(TEST_DATA_DIRECTORY.glob(f"{glob}.json"))
    total_bank = []
    for path in test_bank_files:
        test_bank = json.loads(path.read_text(encoding="utf8"))
        logger.debug(f"{len(test_bank):>3} from {path}")
        total_bank.extend(test_bank)
    return total_bank


def make_ids(entry):
    return entry.get("id") or entry.get("raw")


@pytest.fixture(autouse=False)
def add_output_spacing():
    print("")
    yield
    print("")
