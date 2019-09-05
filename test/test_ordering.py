import re

import pytest

from nominally.parser import Name, pieces_to_words

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


@pytest.mark.parametrize("entry", load_bank("ordering") + BROKEN, ids=make_ids)
def test_meta_no_pre_process_side_effects_these_names(entry):
    _, working = Name.pre_process(entry["raw"])
    assert not any(bool(v) for v in working.values())


@pytest.mark.parametrize("entry", load_bank("ordering") + BROKEN_XFAIL, ids=make_ids)
def test_ordering_unit(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    working = Name.parse_full_name(scrubbed)
    name_dict = {k: " ".join(v) for k, v in working.items()}
    assert name_dict == {key: entry.get(key, "") for key in name_dict.keys()}


@pytest.mark.parametrize("entry", load_bank("ordering") + BROKEN_XFAIL, ids=make_ids)
def test_ordering_end_to_end(entry):
    name_dict = dict(Name(entry["raw"]))
    assert name_dict == {key: entry.get(key, "") for key in name_dict.keys()}


@pytest.mark.parametrize("entry", load_bank("ordering") + BROKEN, ids=make_ids)
def test_suffix_extraction_has_correct_suffixes(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    pieces, suffixes = Name.extract_suffixes(scrubbed)
    assert set(suffixes) == set(entry.get("suffix", "").split())


@pytest.mark.parametrize("entry", load_bank("ordering") + BROKEN, ids=make_ids)
def test_suffix_extraction_returns_appropriate_types(entry):
    # TODO -- add typing instead
    scrubbed, _ = Name.pre_process(entry["raw"])
    pieces, suffixes = Name.extract_suffixes(scrubbed)
    assert all(isinstance(x, str) for x in pieces)


@pytest.mark.parametrize("entry", load_bank("ordering") + BROKEN, ids=make_ids)
def test_suffix_extraction_did_not_mistrack_words(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    pieces, suffixes = Name.extract_suffixes(scrubbed)
    assert set(pieces_to_words(scrubbed)) == set(pieces_to_words(pieces + suffixes))


@pytest.mark.parametrize("entry", load_bank("ordering") + BROKEN, ids=make_ids)
def test_suffix_extraction_maintained_first_last_order(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    pieces, suffixes = Name.extract_suffixes(scrubbed)
    ugly_in = str(scrubbed).replace("'", " ")
    ugly_out = str(pieces).replace("'", " ")
    for marker in (" junior ", " j ", " h c "):
        if marker in ugly_out:
            order_in = ugly_in.index(marker) > ugly_in.index("berger")
            order_out = ugly_out.index(marker) > ugly_out.index("berger")
            assert order_in == order_out


@pytest.mark.parametrize(
    "entry", load_bank("title_ordering") + load_bank("ordering"), ids=make_ids
)
@pytest.mark.xfail(reason="TODO")
def test_title(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    pieces, title = Name.extract_title(scrubbed)
    assert set(title) == set(entry.get("title", "").split())
