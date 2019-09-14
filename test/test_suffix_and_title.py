from collections import defaultdict

import pytest

from nominally.parser import Name

from .conftest import dict_entry_test


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
