"""pytest ./pytest/"""

import json
from pathlib import Path

import pytest

from nominally import Name
from nominally import config

TEST_DATA_DIRECTORY = Path(__file__).parent / "names"


def load_bank(category):
    test_bank_file = (TEST_DATA_DIRECTORY / category).with_suffix(".json")
    test_bank = json.loads(test_bank_file.read_text(encoding="utf8"))
    print(f"Loading {len(test_bank)} cases for {category} from {test_bank_file}.")
    return test_bank


def dict_entry_test(dict_entry):
    hn = Name(dict_entry["raw"])
    expected = {attr: dict_entry.get(attr, "") for attr in hn._members}
    assert hn.as_dict() == expected


def make_ids(entry):
    return entry.get("id") or entry.get("raw")


class TestCoreFunctionality:
    @pytest.mark.parametrize(
        "entry",
        [
            {
                "id": "test_utf8",
                "raw": "de la Véña, Jüan",
                "first": "jüan",
                "last": "de la véña",
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
        ids=lambda x: make_ids(x),
    )
    def test_basics(self, entry):
        dict_entry_test(entry)

    def test_string_output(self):
        hn = Name('de la Véña, Dr. Jüan "Paco", Jr.')
        assert str(hn) == "dr. jüan de la véña jr. (paco)"

    def test_repr_output(self):
        hn = Name('de la Véña, Dr. Jüan "Paco", Jr.')
        assert repr(hn) == (
            "Name({'title': 'dr.', "
            "'first': 'jüan', 'middle': '', 'last': 'de la véña', "
            "'suffix': 'jr.', 'nickname': 'paco'})"
        )

    def test_blank(self):
        hn = Name("")
        assert hn.unparsable
        assert "unparsable" in repr(hn).lower()

    def test_nonblank(self):
        hn = Name("Bob")
        assert not hn.unparsable
        assert "unparsable" not in repr(hn).lower()

    def test_unparsable_are_not_equal(self):
        assert not Name("") == Name("")

    @pytest.mark.parametrize(
        "raw, length", [("Doe-Ray, Dr. John P., Jr", 5), ("John Doe", 2)]
    )
    def test_len(self, raw, length):
        assert len(Name(raw)) == length

    def test_comparison(self):
        hn1 = Name("Doe-Ray, Dr. John P., jr")
        hn2 = Name("Dr. John P. Doe-Ray, jr")
        assert hn1
        assert hn2
        assert hn1 == hn2
        assert hn1 is not hn2
        assert hn1 == "dr. john p. doe-ray jr"
        hn1 = Name("Doe, Dr. John P., Jr")
        hn2 = Name("Dr. John P. Doe-Ray, jr")
        assert hn1 != hn2
        assert hn1 != 0
        assert hn1 != "test"
        assert hn1 != ["test"]
        assert hn1 != {"test": hn2}

    def test_get_full_name_attribute_references_internal_lists(self):
        hn = Name("John Williams")
        hn.first_list = ["larry"]
        assert hn.full_name == "larry williams"

    def test_comparison_case_insensitive(self):
        hn1 = Name("Doe-Ray, Dr. John P., Jr")
        hn2 = Name("dr. john p. doe-Ray, jr")
        assert hn1 == hn2
        assert hn1 is not hn2
        assert hn1 == "dr. john p. doe-ray jr"

    def test_slice(self):
        hn = Name("Doe-Ray, Dr. John P., Jr")
        assert list(hn) == ["dr.", "john", "p.", "doe-ray", "jr"]

    def test_getitem(self):
        hn = Name("Dr. John A. Kenneth Doe, Jr.")
        assert hn["title"] == "dr."
        assert hn["first"] == "john"
        assert hn["last"] == "doe"
        assert hn["middle"] == "a. kenneth"
        assert hn["suffix"] == "jr."


class TestNameBruteForce:
    @pytest.mark.parametrize(
        "entry", load_bank("brute_force"), ids=lambda x: make_ids(x)
    )
    def test_brute(self, entry):
        dict_entry_test(entry)


class TestFirstNameHandling:
    @pytest.mark.parametrize(
        "entry", load_bank("first_name"), ids=lambda x: make_ids(x)
    )
    def test_json_first_name(self, entry):
        dict_entry_test(entry)

    def test_first_name_is_prefix_if_three_parts(self):
        """Not sure how to fix this without breaking Mr and Mrs"""
        hn = Name("Mr. Van Nguyen")
        assert hn.last == "van nguyen"


class TestNameConjunction:
    @pytest.mark.parametrize(
        "entry", load_bank("conjunction"), ids=lambda x: make_ids(x)
    )
    def test_json_conjunction(self, entry):
        dict_entry_test(entry)

    @pytest.mark.xfail
    def test_two_initials_conflict_with_conjunction(self):
        # Supporting this seems to screw up titles with periods in them like M.B.A.
        hn = Name("E.T. Smith")
        assert hn.first == "e."
        assert hn.middle == "t."
        assert hn.last == "smith"

    @pytest.mark.xfail
    def test_four_name_parts_with_suffix_that_could_be_initial_lowercase_no_p(self):
        hn = Name("larry james edward johnson v")
        assert hn.first == "larry"
        assert hn.middle == "james edward"
        assert hn.last == "johnson"
        assert hn.suffix == "v"


class TestNickname:
    @pytest.mark.parametrize("entry", load_bank("nickname"), ids=lambda x: make_ids(x))
    def test_json_nickname(self, entry):
        dict_entry_test(entry)

    # http://code.google.com/p/python-nominally/issues/detail?id=17
    def test_parenthesis_are_removed_from_name(self):
        hn = Name("John Jones (Unknown)")
        assert hn.first == "john"
        assert hn.last == "jones"
        assert hn.nickname != ""

    # http://code.google.com/p/python-nominally/issues/detail?id=17
    # not testing nicknames because we don't actually care about Google Docs here
    def test_duplicate_parenthesis_are_removed_from_name(self):
        hn = Name("John Jones (Google Docs), Jr. (Unknown)")
        assert hn.first == "john"
        assert hn.last == "jones"
        assert hn.suffix == "jr."
        assert hn.nickname != ""


class TestPrefixes:
    @pytest.mark.parametrize("entry", load_bank("prefix"), ids=lambda x: make_ids(x))
    def test_json_prefix(self, entry):
        dict_entry_test(entry)


class TestSuffixes:
    @pytest.mark.parametrize("entry", load_bank("suffix"), ids=lambda x: make_ids(x))
    def test_json_suffix(self, entry):
        dict_entry_test(entry)


class TestTitle:
    @pytest.mark.parametrize("entry", load_bank("title"), ids=lambda x: make_ids(x))
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
        hn = Name(name)
        if len(hn.suffix_list) > 1:
            hn = Name(
                "{title} {first} {middle} {last} {suffix}".format(**hn.as_dict()).split(
                    ","
                )[0]
            )
        hn_dict = hn.as_dict()
        nocomma = Name("{title} {first} {middle} {last} {suffix}".format(**hn_dict))
        lastnamecomma = Name(
            "{last}, {title} {first} {middle} {suffix}".format(**hn_dict)
        )
        if hn.suffix:
            suffixcomma = Name(
                "{title} {first} {middle} {last}, {suffix}".format(**hn_dict)
            )
        if hn.nickname:
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
            if hn.suffix:
                suffixcomma = Name(
                    "{title} {first} {middle} {last}, {suffix} ({nickname})".format(
                        **hn_dict
                    )
                )
        for attr in hn._members:
            assert getattr(hn, attr) == getattr(nocomma, attr)
            assert getattr(hn, attr) == getattr(lastnamecomma, attr)
            if hn.suffix:
                assert getattr(hn, attr) == getattr(suffixcomma, attr)


if __name__ == "__main__":
    import sys

    # Pass through any/all arguments to pytest
    pytest.main(sys.argv)
