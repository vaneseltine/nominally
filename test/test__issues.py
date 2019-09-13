import pytest

from nominally import Name

from .conftest import dict_entry_test


@pytest.mark.xfail(raises=AssertionError)
def issue_22_ambiguous_handling_of_prefixes_in_first_name():
    assert Name("de ook, van ook") == Name("van ook de ook")


@pytest.mark.parametrize(
    "entry",
    [{"raw": "vimes, samuel v", "first": "samuel", "middle": "v", "last": "vimes"}],
)
@pytest.mark.xfail()
def issue_12_make_trailing_v_a_middle_still_broken(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "vimes, sam vii", "first": "sam", "suffix": "vii", "last": "vimes"},
        {"raw": "vimes, samuel x", "first": "samuel", "middle": "x", "last": "vimes"},
    ],
)
def issue_12_make_trailing_x_and_vii_working_by_cheating(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "raw, cleaned",
    [
        ("vimes jr., sam", "vimes, jr, sam"),
        ("sam vimes jr.", "vimes, jr, sam"),
        ("vimes jr., sam (Stoneface)", "vimes, jr, sam (stoneface)"),
    ],
)
@pytest.mark.xfail()
def issue_24_fix_cleaned_names(raw, cleaned):
    assert Name(raw).cleaned == cleaned
