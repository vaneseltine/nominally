import pytest

from nominally import Name, parse_name

from .conftest import make_ids, dict_entry_test


@pytest.mark.parametrize(
    "entry",
    [
        {
            "id": "test_utf8",
            "raw": "de la Véña, Jüan",
            "first": "juan",
            "last": "de la vena",
        },
        {
            "id": "test_conjunction_names",
            "raw": "johnny y",
            "first": "johnny",
            "last": "y",
        },
        {"id": "test_prefixed_names", "raw": "vai la", "first": "vai", "last": "la"},
    ],
    ids=make_ids,
)
def test_basics(entry):
    dict_entry_test(Name, entry)


def test_string_output():
    raw = 'de la Véña, Dr. Jüan "Paco", Jr.'
    n = Name(raw)
    assert str(n) == 'dr juan "paco" de la vena jr'


def test_repr_output():
    n = Name('de la Véña, Dr. Jüan "Paco", Jr.')
    assert repr(n) == (
        "Name({'title': 'dr', "
        "'first': 'juan', 'middle': '', 'last': 'de la vena', "
        "'suffix': 'jr', 'nickname': 'paco'})"
    )


def test_dict_output():
    raw = 'de la Véña, Dr. Jüan "Paco", Jr.'
    n = Name(raw)
    dn = dict(n)
    assert [k for k in n.keys()] == [k for k in dn.keys()]
    assert [v for v in n.values()] == [k for k in dn.values()]


def test_report_output():
    n = Name('de la Véña, Dr. Jüan "Paco", Jr.')
    report = n.report()

    for k in n.keys():
        assert n[k] == report[k]
    assert "list" in report.keys()
    assert isinstance(report["list"], list)
    assert "raw" in report.keys()
    assert isinstance(report["raw"], str)
    assert "parsed" in report.keys()
    assert isinstance(report["parsed"], str)


def test_parse_name_output():
    raw = 'de la Véña, Dr. Jüan "Paco", Jr.'
    n = Name(raw)
    pn = parse_name(str(n))
    assert [k for k in n.keys()] == [k for k in pn.keys()]
    assert [v for v in n.values()] == [k for k in pn.values()]


@pytest.mark.parametrize("raw", ["", ",", "_"])
def test_unparsable_inputs(raw):
    n = Name(raw)
    assert n.unparsable
    assert "unparsable" in repr(n).lower()


def test_nonblank():
    n = Name("Bob")
    assert not n.unparsable
    assert "unparsable" not in repr(n).lower()


def test_unparsable_are_not_equal():
    name1 = Name("")
    name2 = Name("")
    assert name1 != name2


@pytest.mark.parametrize(
    "raw, length", [("Doe-Ray, Dr. John P., Jr", 5), ("John Doe", 2)]
)
def test_len(raw, length):
    assert len(Name(raw)) == length


def test_comparison():
    name1 = Name("Doe-Ray, Dr. John P., jr")
    name2 = Name("Dr. John P. Doe-Ray, jr")
    assert name1
    assert name2
    assert name1 == name2
    assert name1 is not name2
    assert name1 == "dr john p doe-ray jr"
    name1 = Name("Doe, Dr. John P., Jr")
    name2 = Name("Dr. John P. Doe-Ray, jr")
    assert name1 != name2
    assert name1 != 0
    assert name1 != "test"
    assert name1 != ["test"]
    assert name1 != {"test": name2}


def test_comparison_case_insensitive():
    name1 = Name("Doe-Ray, Dr. John P., Jr")
    name2 = Name("dr john p. doe-Ray, jr")
    assert name1 is not name2
    assert name1 == name2
    assert name1 == "dr john p doe-ray jr"


def test_as_list():
    n = Name("Doe-Ray, Dr. John (Doctor Doo) P., Jr")
    assert list(n) == ["dr", "john", "p", "doe-ray", "jr", "doctor doo"]


def test_getitem():
    n = Name("Dr. John A. Kenneth Doe, Jr.")
    assert n["title"] == "dr"
    assert n["first"] == "john"
    assert n["last"] == "doe"
    assert n["middle"] == "a kenneth"
    assert n["suffix"] == "jr"
