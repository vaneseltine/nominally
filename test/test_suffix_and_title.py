import pytest

from nominally.parser import Name, flatten_once

from .conftest import load_bank, make_ids, dict_entry_test


def correct_loose_ordering(pre, post):
    ugly_in = str(pre).replace("'", " ")
    ugly_out = str(post).replace("'", " ")
    for marker in (" junior ", " j ", " h c "):
        if marker in ugly_out:
            assert marker in ugly_in
            order_in = ugly_in.index(marker) > ugly_in.index("berger")
            order_out = ugly_out.index(marker) > ugly_out.index("berger")
            assert order_in == order_out


def test_too_many_name_parts_post_suffix():
    name = Name("johnson, bergholt, stuttley")
    assert name.first == "bergholt"
    assert name.middle == "stuttley"
    assert name.last == "johnson"


def test_way_too_many_name_parts_post_suffix():
    name = Name("johnson, bergholt, stuttley, joonyor")
    assert name.first == "bergholt"
    assert name.middle == "stuttley joonyor"
    assert name.last == "johnson"


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_ordering_end_to_end(entry):
    name_dict = dict(Name(entry["raw"]))
    assert name_dict == {key: entry.get(key, "") for key in name_dict.keys()}


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_suffix_extraction_has_correct_suffixes(entry):
    scrubbed, _d = Name._pre_process(entry["raw"])
    _, suffixes = Name._extract_suffixes(scrubbed)
    assert set(suffixes) == set(entry.get("suffix", "").split())


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_suffix_extraction_did_not_mistrack_words(entry):
    pre_extraction, _d = Name._pre_process(entry["raw"])
    # print("pre", pre_extraction)
    pieces, suffixes = Name._extract_suffixes(pre_extraction)
    post_extraction = flatten_once(pieces) + suffixes
    # print("post", post_extraction)
    pre_comp = set(flatten_once(pre_extraction))
    post_comp = set(post_extraction)
    # print("pre", pre_comp)
    # print("post", post_comp)
    assert pre_comp == post_comp


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_suffix_extraction_maintained_first_last_order(entry):
    scrubbed, _d = Name._pre_process(entry["raw"])
    pre_pieces = scrubbed.copy()
    post_pieces, _ = Name._extract_suffixes(scrubbed)
    correct_loose_ordering(pre_pieces, post_pieces)


@pytest.mark.parametrize(
    "entry", load_bank("title") + load_bank("ordering"), ids=make_ids
)
def test_title_extracts(entry):
    scrubbed, _d = Name._pre_process(entry["raw"])
    _, title = Name._extract_title(scrubbed)
    assert set(title) == set(entry.get("title", "").split())


@pytest.mark.parametrize(
    "entry", load_bank("title") + load_bank("ordering"), ids=make_ids
)
def test_title_ordering(entry):
    scrubbed, _d = Name._pre_process(entry["raw"])
    pre_pieces = scrubbed.copy()
    post_pieces, _ = Name._extract_title(scrubbed)
    if "berg" in entry["raw"]:
        correct_loose_ordering(pre_pieces, post_pieces)


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "v, samuel j", "first": "samuel", "last": "j", "suffix": "v"},
        {"raw": "samuel j v", "first": "samuel", "last": "j", "suffix": "v"},
    ],
)
def issue_8_do_not_make_initials(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "samuel vimes v", "first": "samuel", "last": "vimes", "suffix": "v"},
        {
            "raw": "samuel 'sam' vimes v",
            "first": "samuel",
            "last": "vimes",
            "suffix": "v",
            "nickname": "sam",
        },
    ],
)
def issue_8_make_suffixes(entry):
    dict_entry_test(Name, entry)
