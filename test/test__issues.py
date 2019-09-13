import pytest

from nominally import Name

from .conftest import dict_entry_test


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Allow multiword single quote nicknames while still supporting apostrophes",
)
@pytest.mark.xfail(
    raises=AssertionError,
    reason="Clean each nickname exactly like post-nickname full names",
)
def issue_4_clean_nicknames():
    name = Name("ang%ua (ba%%rky) uberwald")
    assert name.first == "angua"
    assert name.nickname == "barky"


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Probably not, but add a placeholder to keep names separated",
)
def issue_5_leave_non_comma_placeholder_from_nicknames():
    name = Name("angua van (barky) uberwald")
    assert name.last == "uberwald"


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Add nuance to Ph.D. and other inital suffixes to support, e.g., J.R.R.",
)
def issue_7_allow_initials_written_properly():
    n = Name("J.R.R. Tolkien")
    assert n.first == "j"
    assert n.middle == "r r"
    assert n.last == "tolkien"


@pytest.mark.xfail(raises=AssertionError)
def issue_22_ambiguous_handling_of_prefixes_in_first_name():
    assert Name("de ook, van ook") == Name("van ook de ook")


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "vimes, samuel v", "first": "samuel", "middle": "v", "last": "vimes"},
        # {"raw": "vimes, sam vii", "first": "sam", "suffix": "vii", "last": "vimes"},
        {"raw": "vimes, samuel x", "first": "samuel", "middle": "x", "last": "vimes"},
    ],
)
@pytest.mark.xfail(raises=AssertionError)
def issue_12_make_trailing_x_and_v_middle_initials_if_last_up_front(entry):
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
@pytest.mark.xfail(raises=AssertionError)
def issue_15_limit_generational_suffixes(entry):
    dict_entry_test(Name, entry)


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
@pytest.mark.xfail(raises=AssertionError)
def issue_14_support_proper_initials(entry):
    dict_entry_test(Name, entry)
