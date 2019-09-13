import pytest

from nominally import Name

from .conftest import dict_entry_test


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Probably not, but add a placeholder to keep names separated",
)
def issue_5_leave_non_comma_placeholder_from_nicknames():
    name = Name("angua van (barky) uberwald")
    assert name.last == "uberwald"


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
def issue_12_make_trailing_x_and_v_working_by_cheating(entry):
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
        # {"raw": "vimes, sam vii", "first": "sam", "suffix": "vii", "last": "vimes"},
        {"raw": "vimes, samuel x", "first": "samuel", "middle": "x", "last": "vimes"},
    ],
)
def issue_15_limit_generational_suffixes(entry):
    dict_entry_test(Name, entry)
