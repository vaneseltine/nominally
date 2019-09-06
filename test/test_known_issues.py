import pytest

from nominally import Name
from .conftest import dict_entry_test


@pytest.mark.xfail(raises=AssertionError, reason="TBI")
def test_clean_nicknames():
    name = Name("ang%ua (ba%%rky) uberwald")
    assert name.first == "angua"
    assert name.nickname == "barky"


@pytest.mark.xfail(raises=AssertionError, reason="Rare but possible feature")
def test_leave_non_comma_placeholder_from_nicknames():
    name = Name("angua van (barky) uberwald")
    assert name.last == "uberwald"


@pytest.mark.xfail(raises=AttributeError, reason="TODO: Name(Name())")
def test_name_to_name():
    name1 = Name("Dr. Horace 'Ook' Worblehat")
    name2 = Name(name1)
    assert name1 == name2


@pytest.mark.xfail(
    raises=AssertionError, reason="Throw away as mononym? 'Ms. von Uberwald'"
)
def test_first_name_is_prefix_if_three_parts():
    n = Name("Ms. von Uberwald")
    assert n.last == "von uberwald"


@pytest.mark.xfail(
    raises=AssertionError, reason="Support this vs. removing periods for M.B.A., Ph.D."
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
@pytest.mark.xfail(raises=AssertionError, reason="TBD")
def test_distinguish_suffixes_suitably_distinguishable_from_initials(entry):
    dict_entry_test(Name, entry)
