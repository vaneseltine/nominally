import json
from pathlib import Path

import pytest

from nominally.parser import logger

TEST_DATA_DIRECTORY = Path(__file__).parent / "names"


def make_ids(entry):
    return entry.get("id") or entry.get("raw")


def load_bank(category):
    # TODO: glob
    test_bank_file = (TEST_DATA_DIRECTORY / category).with_suffix(".json")
    test_bank = json.loads(test_bank_file.read_text(encoding="utf8"))
    logger.debug(f"{category:>15}: {len(test_bank):>3} from {test_bank_file}")
    return test_bank


@pytest.fixture(autouse=True)
def add_output_spacing():
    print("\n")
    yield
    print("\n")
