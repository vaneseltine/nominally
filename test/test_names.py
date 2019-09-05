"""pytest ./pytest/"""

import json
from pathlib import Path

import pytest

from nominally import Name
from nominally.parser import logger

from .conftest import load_bank, make_ids


def dict_entry_test(entry):
    n = Name(entry["raw"])
    expected = {key: entry.get(key, "") for key in dict(n).keys()}
    assert dict(n) == expected


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
        dict_entry_test(entry)

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
        correct = "dr john p doe-ray jr"
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


class TestNameBruteForce:
    @pytest.mark.parametrize("entry", load_bank("brute_force"), ids=make_ids)
    def test_brute(self, entry):
        dict_entry_test(entry)


class TestFirstNameHandling:
    @pytest.mark.parametrize("entry", load_bank("first_name"), ids=make_ids)
    def test_json_first_name(self, entry):
        dict_entry_test(entry)

    def test_first_name_is_prefix_if_three_parts(self):
        """Not sure how to fix this without breaking Mr and Mrs"""
        n = Name("Mr. Van Nguyen")
        assert n.last == "van nguyen"


class TestNameConjunction:
    @pytest.mark.parametrize("entry", load_bank("conjunction"), ids=make_ids)
    def test_json_conjunction(self, entry):
        dict_entry_test(entry)

    @pytest.mark.xfail(reason="Support this vs. removing periods for M.B.A., Ph.D.")
    def test_two_initials_conflict_with_conjunction(self):
        n = Name("J.R.R. Tolkien")
        assert n.first == "j"
        assert n.middle == "r r"
        assert n.last == "tolkien"

    @pytest.mark.xfail
    def test_four_name_parts_with_suffix_that_could_be_initial_lowercase_no_p(self):
        n = Name("larry james edward johnson v")
        assert n.first == "larry"
        assert n.middle == "james edward"
        assert n.last == "johnson"
        assert n.suffix == "v"


class TestNickname:
    @pytest.mark.parametrize("entry", load_bank("nickname"), ids=make_ids)
    def test_json_nickname(self, entry):
        dict_entry_test(entry)

    def test_parenthesis_are_removed_from_name(self):
        n = Name("John Jones (Unknown)")
        assert n.first == "john"
        assert n.last == "jones"
        assert n.nickname != ""

    # not testing nicknames because we don't actually care about Google Docs here
    def test_duplicate_parenthesis_are_removed_from_name(self):
        n = Name("John Jones (Google Docs), Jr. (Unknown)")
        assert n.first == "john"
        assert n.last == "jones"
        assert n.suffix == "jr"
        assert n.nickname != ""


class TestPrefixes:
    @pytest.mark.parametrize("entry", load_bank("prefix"), ids=make_ids)
    def test_json_prefix(self, entry):
        dict_entry_test(entry)


class TestSuffixes:
    @pytest.mark.parametrize("entry", load_bank("suffix"), ids=make_ids)
    def test_json_suffix(self, entry):
        dict_entry_test(entry)


class TestTitle:
    @pytest.mark.parametrize("entry", load_bank("title"), ids=make_ids)
    def test_json_title(self, entry):
        dict_entry_test(entry)


class TestNameVariations:
    """Test automated variations of raw names in the 'brute_force' bank.

    Helps test that the 3 code trees work the same"""

    @pytest.mark.parametrize("name", load_bank("brute_force"))
    def test_json_variations(self, name):
        self.run_variations(name["raw"])

    def run_variations(self, name):
        """ Run several variations

        This is a separate function so that individual non-parametrized tests can be
        added if desired.
        """
        n = Name(name)
        if len(n.suffix.split()) > 1:
            n = Name(
                "{title} {first} {middle} {last} {suffix}".format(**dict(n)).split(",")[
                    0
                ]
            )
        hn_dict = dict(n)
        nocomma = Name("{title} {first} {middle} {last} {suffix}".format(**hn_dict))
        lastnamecomma = Name(
            "{last}, {title} {first} {middle} {suffix}".format(**hn_dict)
        )
        if n.suffix:
            suffixcomma = Name(
                "{title} {first} {middle} {last}, {suffix}".format(**hn_dict)
            )
        if n.nickname:
            nocomma = Name(
                "{title} {first} {middle} {last} {suffix} ({nickname})".format(
                    **hn_dict
                )
            )
            lastnamecomma = Name(
                "{last}, {title} {first} {middle} {suffix} ({nickname})".format(
                    **hn_dict
                )
            )
            if n.suffix:
                suffixcomma = Name(
                    "{title} {first} {middle} {last}, {suffix} ({nickname})".format(
                        **hn_dict
                    )
                )
        for key in n.keys():
            assert n[key] == nocomma[key]
            assert getattr(n, key) == getattr(nocomma, key)
            assert n[key] == lastnamecomma[key]
            assert getattr(n, key) == getattr(lastnamecomma, key)
            if n.suffix:
                assert n[key] == suffixcomma[key]
                assert getattr(n, key) == getattr(suffixcomma, key)


if __name__ == "__main__":
    import sys

    # Pass through any/all arguments to pytest
    pytest.main(sys.argv)
