import json
from pathlib import Path

import pytest

from nominally.parser import logger

TEST_DATA_DIRECTORY = Path(__file__).parent / "names"


def dict_entry_test(testclass, entry):
    n = testclass(entry["raw"])
    expected = {key: entry.get(key, "") for key in dict(n).keys()}
    assert dict(n) == expected


def load_bank(category):
    test_bank_file = (TEST_DATA_DIRECTORY / category).with_suffix(".json")
    test_bank = json.loads(test_bank_file.read_text(encoding="utf8"))
    logger.debug(f"{category:>15}: {len(test_bank):>3} from {test_bank_file}")
    return test_bank


def make_ids(entry):
    return entry.get("id") or entry.get("raw")


def pieces_to_words(pieces):
    return " ".join(pieces).split()


def verify_approximate_ordering_of_leftovers(pre, post):
    ugly_in = str(pre).replace("'", " ")
    ugly_out = str(post).replace("'", " ")
    for marker in (" junior ", " j ", " h c "):
        if marker in ugly_out:
            assert marker in ugly_in
            order_in = ugly_in.index(marker) > ugly_in.index("berger")
            order_out = ugly_out.index(marker) > ugly_out.index("berger")
            logger.warning(f"pre:  {ugly_in}")
            logger.warning(f"post: {ugly_out}")
            assert order_in == order_out


@pytest.fixture(autouse=True)
def add_output_spacing():
    print("\n")
    yield
    print("\n")
