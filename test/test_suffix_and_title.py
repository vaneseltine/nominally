import pytest

from collections import defaultdict
from nominally.parser import Name, flatten_once

from .conftest import dict_entry_test, load_bank, make_ids


def fake_working(**kwargs):
    fresh = {k: [] for k in Name._keys}
    return defaultdict(list, {**kwargs, **fresh})


@pytest.mark.parametrize(
    "args, outs, outwork",
    [
        [("bob", fake_working()), "bob", []],
        [("bob ph.d.", fake_working()), "bob", ["phd"]],
        [("bob ph.d.", fake_working()), "bob", ["phd"]],
    ],
)
def test_sweep_suffixes(args, outs, outwork):
    observed_string, observed_working = Name._sweep_suffixes(*args)
    assert observed_string.strip() == outs
    assert observed_working["suffix"] == outwork


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
    name = Name(entry["raw"])
    for key in ["first", "middle", "last"]:
        assert entry.get(key, "") == name[key]


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_suffix_extraction_has_correct_suffixes(entry):
    scrubbed, working = Name._pre_process(entry["raw"])
    _, working = Name._extract_suffixes(scrubbed, working)
    assert set(working["suffix"] + working["generational"]) == set(
        entry.get("suffix", "").split()
    )


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_suffix_extraction_did_not_mistrack_words(entry):
    pre_extraction, _d = Name._pre_process(entry["raw"])
    pieces, working = Name._extract_suffixes(pre_extraction, fake_working())
    post_extraction = flatten_once(pieces) + working["suffix"] + working["generational"]
    pre_comp = set(flatten_once(pre_extraction))
    post_comp = set(post_extraction)
    assert pre_comp == post_comp


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_suffix_extraction_maintained_first_last_order(entry):
    scrubbed, _d = Name._pre_process(entry["raw"])
    pre_pieces = scrubbed.copy()
    post_pieces, _ = Name._extract_suffixes(scrubbed, fake_working())
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


def issue_7_allow_initials_written_properly():
    n = Name("J.R.R. Tolkien")
    assert n.first == "j"
    assert n.middle == "r r"
    assert n.last == "tolkien"


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "J.R.R. Tolkien", "first": "j", "middle": "r r", "last": "tolkien"},
        {
            "raw": "Tolkien, J.R. Jr.",
            "first": "j",
            "middle": "r",
            "last": "tolkien",
            "suffix": "jr",
        },
    ],
)
def issue_14_support_proper_initials(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "entry",
    [
        {
            "raw": "samuel vimes v jr",
            "first": "samuel",
            "middle": "v",
            "last": "vimes",
            "suffix": "jr",
        },
        {"raw": "vimes, sam vii", "first": "sam", "suffix": "vii", "last": "vimes"},
        {"raw": "vimes, samuel x", "first": "samuel", "middle": "x", "last": "vimes"},
    ],
)
def issue_15_limit_generational_suffixes(entry):
    dict_entry_test(Name, entry)
