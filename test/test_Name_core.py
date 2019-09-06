import pytest

from nominally import Name

from .conftest import make_ids, dict_entry_test


class TestCoreFunctionality:
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
            {
                "id": "test_prefixed_names",
                "raw": "vai la",
                "first": "vai",
                "last": "la",
            },
        ],
        ids=make_ids,
    )
    def test_basics(self, entry):
        dict_entry_test(Name, entry)

    def test_string_output(self):
        n = Name('de la Véña, Dr. Jüan "Paco", Jr.')
        assert str(n) == 'dr juan "paco" de la vena jr'

    def test_repr_output(self):
        n = Name('de la Véña, Dr. Jüan "Paco", Jr.')
        assert repr(n) == (
            "Name({'title': 'dr', "
            "'first': 'juan', 'middle': '', 'last': 'de la vena', "
            "'suffix': 'jr', 'nickname': 'paco'})"
        )

    def test_blank(self):
        n = Name("")
        assert n.unparsable
        assert "unparsable" in repr(n).lower()

    def test_nonblank(self):
        n = Name("Bob")
        assert not n.unparsable
        assert "unparsable" not in repr(n).lower()

    def test_unparsable_are_not_equal(self):
        name1 = Name("")
        name2 = Name("")
        assert name1 != name2

    @pytest.mark.parametrize(
        "raw, length", [("Doe-Ray, Dr. John P., Jr", 5), ("John Doe", 2)]
    )
    def test_len(self, raw, length):
        assert len(Name(raw)) == length

    def test_comparison(self):
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

    def test_comparison_case_insensitive(self):
        name1 = Name("Doe-Ray, Dr. John P., Jr")
        name2 = Name("dr john p. doe-Ray, jr")
        assert name1 is not name2
        assert name1 == name2
        assert name1 == "dr john p doe-ray jr"

    def test_as_list(self):
        n = Name("Doe-Ray, Dr. John (Doctor Doo) P., Jr")
        assert list(n) == ["dr", "john", "p", "doe-ray", "jr", "doctor doo"]

    def test_getitem(self):
        n = Name("Dr. John A. Kenneth Doe, Jr.")
        assert n["title"] == "dr"
        assert n["first"] == "john"
        assert n["last"] == "doe"
        assert n["middle"] == "a kenneth"
        assert n["suffix"] == "jr"
