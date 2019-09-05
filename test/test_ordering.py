import pytest
import re
from nominally.parser import Name

from .conftest import load_bank, make_ids

BROKEN = [
    pytest.param({"raw": "goatberger, phd., junior h. c."}, marks=pytest.mark.xfail()),
    pytest.param({"raw": "goatberger, ii., j. h. c."}, marks=pytest.mark.xfail()),
    pytest.param({"raw": "goatberger, junior, j. h. c."}, marks=pytest.mark.xfail()),
    pytest.param({"raw": "goatberger, junior, j."}, marks=pytest.mark.xfail()),
]


@pytest.fixture(autouse=False)
def add_spacing():
    print("\n")
    yield
    print("\n")


@pytest.mark.parametrize("entry", load_bank("arrangements") + BROKEN, ids=make_ids)
@pytest.mark.parametrize("pyramid", ["end-to-end", "unit"])
def test_arrangements(entry, pyramid):

    if pyramid == "unit":
        empty = {k: [] for k in Name.keys()}
        # relevant part of pre_process()
        remaining = re.split(r"\s*,\s*", (entry["raw"].replace(".", "")))
        working = Name.parse_full_name(remaining, working=empty)
        name_dict = {k: " ".join(v) for k, v in working.items()}
    else:
        name_dict = dict(Name(entry["raw"]))

    expected = {key: entry.get(key, "") for key in name_dict.keys()}
    assert name_dict == expected


@pytest.mark.parametrize("entry", load_bank("arrangements") + BROKEN, ids=make_ids)
@pytest.mark.xfail(reason="working")
def test_suffix_extraction(entry):
    assert Name.extract_suffixes(entry["raw"]) == "pie"

