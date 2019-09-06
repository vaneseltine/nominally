import pytest

from nominally import Name


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


@pytest.mark.xfail(raises=AssertionError)
def test_do_not_take_initial_slash_suffix_as_last_name_with_good_names_later():
    n = Name("larry james edward johnson v")
    assert n.first == "larry"
    assert n.middle == "james edward"
    assert n.last == "johnson"
    assert n.suffix == "v"
