from collections import defaultdict

import pytest

from nominally.parser import Name

from .conftest import dict_entry_test


def fake_working(**kwargs):
    fresh = {k: [] for k in Name._keys}
    return defaultdict(list, {**kwargs, **fresh})


# @pytest.mark.xfail(reason="Breaking unit tests")
@pytest.mark.parametrize(
    "incoming, outs, outwork",
    [
        ["bob b. bob", "bob b. bob", []],
        ["bob b. bob ph.d.", "bob b. bob", ["phd"]],
        ["bob b. bob ph.d.", "bob b. bob", ["phd"]],
    ],
)
def test_sweep_suffixes(incoming, outs, outwork):
    bob = Name()
    observed_string = bob._sweep_suffixes(incoming)
    assert observed_string.strip() == outs
    assert bob.detail["suffix"] == outwork


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


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "v, samuel j", "first": "samuel", "last": "v", "middle": "j"},
        {"raw": "samuel j v", "first": "samuel", "last": "v", "middle": "j"},
        {"raw": "samuel vimes v", "first": "samuel", "middle": "vimes", "last": "v"},
        {
            "raw": "samuel 'sam' vimes v",
            "first": "samuel",
            "middle": "vimes",
            "last": "v",
            "nickname": "sam",
        },
    ],
)
def issue_8_final_suffix_resolutions_updated_for_issue_12(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "vimes, sam v", "first": "sam", "middle": "v", "last": "vimes"},
        {"raw": "vimes, sam bob v", "first": "sam", "middle": "bob v", "last": "vimes"},
        {"raw": "sam v vimes", "first": "sam", "middle": "v", "last": "vimes"},
        {"raw": "sam v bob vimes", "first": "sam", "middle": "v bob", "last": "vimes"},
    ],
)
def issue_12_fix_trailing_v(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "entry",
    [
        {
            "raw": "vimes, samuel vii",
            "first": "samuel",
            "middle": "vii",
            "last": "vimes",
        },
        {"raw": "vimes, samuel x", "first": "samuel", "middle": "x", "last": "vimes"},
    ],
)
def issue_12_make_trailing_x_and_vii_working_by_removing_suffix_options(entry):
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
            "middle": "vimes",
            "last": "v",
            "suffix": "jr",
        },
        {"raw": "vimes, samuel x", "first": "samuel", "middle": "x", "last": "vimes"},
    ],
)
def issue_15_limit_generational_suffixes(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "sam i vimes", "first": "sam", "middle": "i", "last": "vimes"},
        {"raw": "sam ii vimes", "first": "sam", "suffix": "ii", "last": "vimes"},
        {"raw": "sam iii vimes", "first": "sam", "suffix": "iii", "last": "vimes"},
        {"raw": "sam iv vimes", "first": "sam", "suffix": "iv", "last": "vimes"},
    ],
)
def issue_25_more_suffix_issues(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "entry",
    [
        {
            "raw": "junior e. i vimes",
            "first": "junior",
            "middle": "e i",
            "last": "vimes",
        },
        {
            "raw": "junior e. ii vimes",
            "first": "junior",
            "middle": "e",
            "suffix": "ii",
            "last": "vimes",
        },
        {
            "raw": "junior e. iii vimes",
            "first": "junior",
            "middle": "e",
            "suffix": "iii",
            "last": "vimes",
        },
        {
            "raw": "junior e. iv vimes",
            "first": "junior",
            "middle": "e",
            "suffix": "iv",
            "last": "vimes",
        },
    ],
)
def test_junior_with_gen_suffix(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "pieceslist",
    [
        [["sam", "vimes", "junior"]],
        [["sam", "junior", "vimes"]],
        [["sam", "junior", "vimes"]],
        [["junior", "vimes"], ["sam"]],
        [["vimes", "junior"], ["sam"]],
        [["vimes"], ["junior"], ["sam"]],
        [["junior"], ["vimes"], ["sam"]],
        [["vimes"], ["sam"], ["junior"]],
    ],
)
def test_unit_grab_junior(pieceslist):
    blank = Name()
    _ = blank._grab_junior(pieceslist)
    assert "junior" in blank.detail["suffix"]


@pytest.mark.parametrize(
    "pieceslist",
    [[["junior", "vimes"]], [["junior", "sam", "vimes"]], [["junior"], ["vimes"]]],
)
def test_unit_do_not_grab_junior(pieceslist):
    blank = Name()
    _ = blank._grab_junior(pieceslist)
    assert "junior" not in blank.detail["suffix"]


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "j smith 4th", "last": "smith", "first": "j", "suffix": "4th"},
        {"raw": "j smith 5th", "last": "smith", "first": "j", "suffix": "5th"},
        {"raw": "j smith 6th", "last": "smith", "first": "j", "suffix": "6th"},
        {"raw": "j smith 7th", "last": "smith", "first": "j", "suffix": "7th"},
        {"raw": "j smith 8th", "last": "smith", "first": "j", "suffix": "8th"},
        {"raw": "j smith 9th", "last": "smith", "first": "j", "suffix": "9th"},
        {"raw": "j smith 10th", "last": "smith", "first": "j", "suffix": "10th"},
    ],
)
def issue_31_allow_ordinals(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "entry",
    [
        {
            "raw": "bah loney, junior oni r q x",
            "last": "bah loney",
            "first": "junior",
            "middle": "oni r q x",
        }
    ],
)
def test_last_names_and_junior_non_prefixed_(entry):
    dict_entry_test(Name, entry)
