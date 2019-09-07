import pytest

from nominally import Name

from .conftest import dict_entry_test


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Allow multiword single quote nicknames while still supporting apostrophes",
)
def allow_outer_only_single_quotes():
    name = Name("Gwinifer 'Old Mother' Blackcap")
    assert name.nickname == "old mother"


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Clean each nickname exactly like post-nickname full names",
)
def test_clean_nicknames():
    name = Name("ang%ua (ba%%rky) uberwald")
    assert name.first == "angua"
    assert name.nickname == "barky"


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Probably not, but add a placeholder to keep names separated",
)
def test_leave_non_comma_placeholder_from_nicknames():
    name = Name("angua van (barky) uberwald")
    assert name.last == "uberwald"


@pytest.mark.xfail(
    raises=AttributeError,
    reason="Initiate new Name by passing an existing instance of Name",
)
def test_name_to_name():
    name1 = Name("Dr. Horace 'Ook' Worblehat")
    name2 = Name(name1)
    assert name1 == name2


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Probably accept that we can't have 'Ms. von Uberwald' and Ms. Van Eseltine",
)
def test_first_name_is_prefix_if_three_parts():
    n = Name("Ms. von Uberwald")
    assert n.last == "von uberwald"


@pytest.mark.xfail(
    raises=AssertionError,
    reason="Add nuance to Ph.D. and other inital suffixes to support, e.g., J.R.R.",
)
def test_allow_initials_written_properly():
    n = Name("J.R.R. Tolkien")
    assert n.first == "j"
    assert n.middle == "r r"
    assert n.last == "tolkien"


@pytest.mark.parametrize(
    "entry",
    [
        {"raw": "v, samuel j", "first": "samuel", "middle": "j", "last": "v"},
        {"raw": "samuel j v", "first": "samuel", "middle": "j", "last": "v"},
    ],
)
@pytest.mark.xfail(
    raises=AssertionError,
    reason="Find some good ways to make suffixes when initials are unlikely.",
)
def test_distinguish_suffixes_suitably_distinguishable_from_initials(entry):
    dict_entry_test(Name, entry)
