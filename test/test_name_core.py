import pytest

from nominally import Name, parse_name

BLANKINSOPS = [
    "Blankinsop, Jr., Mr. James 'Jimmy'",
    "Blankinsop Jr., Mr. James (Jimmy)",
    "Mr. James (Jimmy) Blankinsop, Jr.,",
    "mr. james (jimmy) blankinsop jr.,",
]


def test_string_output():
    raw = "Blankinsop, Jr., Mr. James Juju (Jimmy)"
    n = Name(raw)
    assert str(n) == "blankinsop, mr james juju jr (jimmy)"


def test_repr_output():
    n = Name('de la Véña, Dr. Jüan "Paco", Jr.')
    assert repr(n) == (
        "Name({'title': 'dr', "
        "'first': 'juan', 'middle': '', 'last': 'de la vena', "
        "'suffix': 'jr', 'nickname': 'paco'})"
    )


@pytest.mark.parametrize(
    "raw, cleaned",
    [
        ("vimes jr., sam", {"vimes, sam", "jr"}),
        ("sam vimes jr.", {"sam vimes", "jr"}),
        ("vimes jr., sam (Stoneface)", {"vimes, sam", "jr", "stoneface"}),
    ],
)
def issue_24_cleaned_output_as_sets(raw, cleaned):
    assert Name(raw).cleaned == cleaned


def test_dict_output():
    name = Name('de la Véña, Dr. Jüan "Paco" Jeff, Jr.')
    dicted = dict(name)
    assert dict(dicted) == dict(name) == name


def test_report_output():
    name = Name('de la Véña, Dr. Jüan "Paco", Jr.')
    report = name.report()

    for k in name.keys():
        assert name[k] == report[k]
    assert all(k in report for k in ("list", "raw", "parsed"))


def test_parse_name_output():
    raw = "Blankinsop, Jr., Mr. James 'Jimmy'"
    assert parse_name(raw) == Name(raw)


@pytest.mark.parametrize("raw", ["", ",", "_", "2"])
def test_some_message_about_parsability(raw):
    n = Name(raw)
    assert not n.parsable
    assert "pars" in repr(n).lower()


@pytest.mark.parametrize("raw", ["Pepperpot", "J P", "P"])
def test_no_message_about_parsability(raw):
    n = Name(raw)
    assert n.parsable
    assert "pars" not in repr(n).lower()


@pytest.mark.parametrize("name", ["", "#$", "  "])
def test_no_equality_of_unparsables(name):
    name1 = Name(name)
    name2 = Name(name)
    assert name1 != name2


@pytest.mark.parametrize("raw_one", BLANKINSOPS)
@pytest.mark.parametrize("raw_two", BLANKINSOPS)
def test_equality(raw_one, raw_two):
    name_one = Name(raw_one)
    name_two = Name(raw_two)
    assert name_one and name_two
    assert name_one == name_two
    assert name_one is not name_two


def test_dict_equality():
    name = Name("Mr. James (Jimmy) Barnaby Betrothed Blankinsop, Jr.,")
    assert dict(dict(name)) == dict(name) == name
    assert name == {
        "first": "james",
        "last": "blankinsop",
        "middle": "barnaby betrothed",
        "nickname": "jimmy",
        "suffix": "jr",
        "title": "mr",
    }


@pytest.mark.parametrize(
    "other",
    [
        0,
        1,
        True,
        "string",
        ("string tuple",),
        ["string list"],
        {"first": "james"},
        Name("Mr. James (Evil Jimmy) Blankinsop, Jr.,"),
        {
            "first": "james",
            "last": "blankinsop",
            "middle": "barnaby betrothed",
            "nickname": "jimmy",
            "suffix": "jr",
            "title": "mr",
            "additional field": "uh-oh",
        },
    ],
)
def test_inequality(other):
    name = Name("Mr. James (Jimmy) Blankinsop, Jr.,")
    assert name != other


def test_as_list():
    n = Name("Mr. James (Jimmy) Barnaby Betrothed Blankinsop, Jr.,")
    assert list(n.values()) == [
        "mr",
        "james",
        "barnaby betrothed",
        "blankinsop",
        "jr",
        "jimmy",
    ]


def test_via_getitem():
    n = Name("Mr. James (Jimmy) Barnaby Betrothed Blankinsop, Jr.,")
    assert n["title"] == "mr"
    assert n["first"] == "james"
    assert n["last"] == "blankinsop"
    assert n["middle"] == "barnaby betrothed"
    assert n["suffix"] == "jr"
    assert n["nickname"] == "jimmy"


def test_via_attribute():
    n = Name("Mr. James (Jimmy) Barnaby Betrothed Blankinsop, Jr.,")
    assert n.title == "mr"
    assert n.first == "james"
    assert n.last == "blankinsop"
    assert n.middle == "barnaby betrothed"
    assert n.suffix == "jr"
    assert n.nickname == "jimmy"


def test_do_not_invent_attributes():
    n = Name("Mr. James (Jimmy) Barnaby Betrothed Blankinsop, Jr.,")
    with pytest.raises(AttributeError):
        assert n.herring


def issue_6_name_to_name():
    name1 = Name("Dr. Horace 'Ook' Worblehat")
    name2 = Name(name1)
    assert name1 == name2


def issue_3_allow_outer_only_single_quotes():
    name = Name("Gwinifer 'Old Mother' Blackcap")
    assert name.nickname == "old mother"


def issue_3_do_not_overcapture_single_quotes():
    name = Name("Gwinifer O'Canny Nutella' Blackcap")
    assert not name.nickname
