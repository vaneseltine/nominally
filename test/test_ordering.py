import pytest
import re
from nominally.parser import Name, pieces_to_words, logger

from .conftest import load_bank, make_ids

BROKEN = [
    {
        "raw": "sheepberger, phd., junior h. c.",
        "first": "junior",
        "middle": "h c",
        "last": "sheepberger",
        "suffix": "phd",
    },
    {
        "raw": "sheepberger, ii., j. h. c.",
        "first": "j",
        "middle": "h c",
        "last": "sheepberger",
        "suffix": "ii",
    },
    {
        "raw": "sheepberger, junior, j. h. c.",
        "first": "j",
        "middle": "h c",
        "last": "sheepberger",
        "suffix": "junior",
    },
    {
        "raw": "sheepberger, junior, j.",
        "first": "j",
        "last": "sheepberger",
        "suffix": "junior",
    },
]

BROKEN_XFAIL = [pytest.param(x, marks=pytest.mark.xfail()) for x in BROKEN]


@pytest.mark.parametrize("entry", load_bank("ordering") + BROKEN_XFAIL, ids=make_ids)
@pytest.mark.parametrize("pyramid", ["end-to-end", "unit"])
def test_ordering(entry, pyramid):

    if pyramid == "unit":
        empty = {k: [] for k in Name.keys()}
        # relevant part of pre_process()
        remaining = re.split(r"\s*,\s*", (entry["raw"].replace(".", "")))
        working = Name.parse_full_name(remaining)
        name_dict = {k: " ".join(v) for k, v in working.items()}
    else:
        name_dict = dict(Name(entry["raw"]))

    expected = {key: entry.get(key, "") for key in name_dict.keys()}
    assert name_dict == expected


@pytest.mark.parametrize("entry", load_bank("ordering") + BROKEN, ids=make_ids)
# @pytest.mark.xfail(reason="working")
def test_suffix_extraction(entry):
    scrubbed, fake_working = Name.pre_process(entry["raw"])

    # pre_processing didn't have any weird side effects to worry about
    assert not any(bool(v) for v in fake_working.values())

    pieces, suffixes = Name.extract_suffixes(scrubbed)
    logger.warning(f"FINAL {pieces}")
    logger.warning(f"FINAL {suffixes}")

    # The suffixes are what we want
    assert set(suffixes) == set(entry.get("suffix", "").split())
    # We got back a sequence of strings for the pieces
    assert all(isinstance(x, str) for x in pieces)
    # No words were lost or gained
    assert set(pieces_to_words(scrubbed)) == set(pieces_to_words(pieces + suffixes))

    ugly_in = str(scrubbed)
    ugly_out = str(pieces)
    if "junior" in ugly_out:
        last_name_first_in = ugly_in.index("junior") > ugly_in.index("berg")
        last_name_first_out = ugly_out.index("junior") > ugly_out.index("berg")
        print(f"last name is first: {last_name_first_in}")
        print(f"last name is first: {last_name_first_out}")
        assert last_name_first_in == last_name_first_out

