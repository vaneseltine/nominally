# -*- coding: utf-8 -*-
"""pytest ./pytest/"""

import json
from pathlib import Path

import pytest

from nominally import HumanName
from nominally.config import Constants, CONSTANTS

TEST_DATA_DIRECTORY = Path(__file__).parent / "names"


def load_bank(category):
    test_bank_file = (TEST_DATA_DIRECTORY / category).with_suffix(".json")
    test_bank = json.loads(test_bank_file.read_text(encoding="utf8"))
    print(
        "Loading {} cases for {} from {}.".format(
            len(test_bank), category, test_bank_file.resolve()
        )
    )
    return test_bank


def dict_entry_test(dict_entry):
    hn = HumanName(dict_entry["raw"])
    print(hn)
    for attr in hn._members:
        actual = getattr(hn, attr)
        expected = dict_entry.get(attr, "")
        assert actual == expected


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
        hn = HumanName("de la Véña, Jüan")
        print(hn)
        print(repr(hn))

    def test_blank(self):
        hn = HumanName("")
        assert hn.unparsable
        assert "unparsable" in repr(hn).lower()

    def test_nonblank(self):
        hn = HumanName("Bob")
        assert not hn.unparsable
        assert "unparsable" not in repr(hn).lower()

    @pytest.mark.parametrize(
        "raw, length", [("Doe-Ray, Dr. John P., CLU, CFP, LUTC", 5), ("John Doe", 2)]
    )
    def test_len(self, raw, length):
        assert len(HumanName(raw)) == length

    def test_comparison(self):
        hn1 = HumanName("Doe-Ray, Dr. John P., CLU, CFP, LUTC")
        hn2 = HumanName("Dr. John P. Doe-Ray, CLU, CFP, LUTC")
        assert hn1
        assert hn2
        assert hn1 == hn2
        assert hn1 is not hn2
        assert hn1 == "dr. john p. doe-ray clu, cfp, lutc"
        hn1 = HumanName("Doe, Dr. John P., CLU, CFP, LUTC")
        hn2 = HumanName("Dr. John P. Doe-Ray, CLU, CFP, LUTC")
        assert hn1 != hn2
        assert hn1 != 0
        assert hn1 != "test"
        assert hn1 != ["test"]
        assert hn1 != {"test": hn2}

    def test_assignment_to_full_name(self):
        hn = HumanName("John A. Kenneth Doe, Jr.")
        assert hn.first == "john"
        assert hn.last == "doe"
        assert hn.middle == "a. kenneth"
        assert hn.suffix == "jr."
        hn.full_name = "Juan Velasquez y Garcia III"
        assert hn.first == "juan"
        assert hn.last == "velasquez y garcia"
        assert hn.suffix == "iii"

    def test_get_full_name_attribute_references_internal_lists(self):
        hn = HumanName("John Williams")
        hn.first_list = ["larry"]
        assert hn.full_name == "larry williams"

    def test_assignment_to_attribute(self):
        hn = HumanName("John A. Kenneth Doe, Jr.")
        hn.last = "de la vega"
        assert hn.last == "de la vega"
        hn.title = "test"
        assert hn.title == "test"
        hn.first = "test"
        assert hn.first == "test"
        hn.middle = "test"
        assert hn.middle == "test"
        hn.suffix = "test"
        assert hn.suffix == "test"
        with pytest.raises(TypeError):
            hn.suffix = [["test"]]
        with pytest.raises(TypeError):
            hn.suffix = {"test": "test"}

    def test_assign_list_to_attribute(self):
        hn = HumanName("John A. Kenneth Doe, Jr.")
        hn.title = ["test1", "test2"]
        assert hn.title == "test1 test2"
        hn.first = ["test3", "test4"]
        assert hn.first == "test3 test4"
        hn.middle = ["test5", "test6", "test7"]
        assert hn.middle == "test5 test6 test7"
        hn.last = ["test8", "test9", "test10"]
        assert hn.last == "test8 test9 test10"
        hn.suffix = ["test"]
        assert hn.suffix == "test"

    def test_comparison_case_insensitive(self):
        hn1 = HumanName("Doe-Ray, Dr. John P., CLU, CFP, LUTC")
        hn2 = HumanName("dr. john p. doe-Ray, CLU, CFP, LUTC")
        assert hn1 == hn2
        assert hn1 is not hn2
        assert hn1 == "dr. john p. doe-ray clu, cfp, lutc"

    def test_slice(self):
        hn = HumanName("Doe-Ray, Dr. John P., CLU, CFP, LUTC")
        assert list(hn) == ["dr.", "john", "p.", "doe-ray", "clu, cfp, lutc"]
        assert hn[1:] == ["john", "p.", "doe-ray", "clu, cfp, lutc", ""]
        assert hn[1:-2] == ["john", "p.", "doe-ray"]

    def test_getitem(self):
        hn = HumanName("Dr. John A. Kenneth Doe, Jr.")
        assert hn["title"] == "dr."
        assert hn["first"] == "john"
        assert hn["last"] == "doe"
        assert hn["middle"] == "a. kenneth"
        assert hn["suffix"] == "jr."

    def test_setitem(self):
        hn = HumanName("Dr. John A. Kenneth Doe, Jr.")
        hn["title"] = "test"
        assert hn["title"] == "test"
        hn["last"] = ["test", "test2"]
        assert hn["last"] == "test test2"
        with pytest.raises(TypeError):
            hn["suffix"] = [["test"]]
        with pytest.raises(TypeError):
            hn["suffix"] = {"test": "test"}

    def test_surnames_list_attribute(self):
        hn = HumanName("John Edgar Casey Williams III")
        assert hn.surnames_list == ["edgar", "casey", "williams"]

    def test_surnames_attribute(self):
        hn = HumanName("John Edgar Casey Williams III")
        assert hn.surnames == "edgar casey williams"


class TestHumanNameBruteForce:
    # This fixes a bug in test115, which is not testing the suffix
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

    @pytest.mark.xfail
    def test_first_name_is_prefix_if_three_parts(self):
        """Not sure how to fix this without breaking Mr and Mrs"""
        hn = HumanName("Mr. Van Nguyen")
        assert hn.first == "van"
        assert hn.last == "nguyen"


class TestHumanNameConjunction:
    @pytest.mark.parametrize(
        "entry", load_bank("conjunction"), ids=lambda x: make_ids(x)
    )
    def test_json_conjunction(self, entry):
        dict_entry_test(entry)

    @pytest.mark.xfail
    def test_two_initials_conflict_with_conjunction(self):
        # Supporting this seems to screw up titles with periods in them like M.B.A.
        hn = HumanName("E.T. Smith")
        assert hn.first == "e."
        assert hn.middle == "t."
        assert hn.last == "smith"

    @pytest.mark.xfail
    def test_title_with_three_part_name_last_initial_is_suffix_uppercase_no_p(self):
        hn = HumanName("king john alexander v")
        assert hn.title == "king"
        assert hn.first == "john"
        assert hn.last == "alexander"
        assert hn.suffix == "v"

    @pytest.mark.xfail
    def test_four_name_parts_with_suffix_that_could_be_initial_lowercase_no_p(self):
        hn = HumanName("larry james edward johnson v")
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
        hn = HumanName("John Jones (Unknown)")
        assert hn.first == "john"
        assert hn.last == "jones"
        assert hn.nickname != ""

    # http://code.google.com/p/python-nominally/issues/detail?id=17
    # not testing nicknames because we don't actually care about Google Docs here
    def test_duplicate_parenthesis_are_removed_from_name(self):
        hn = HumanName("John Jones (Google Docs), Jr. (Unknown)")
        assert hn.first == "john"
        assert hn.last == "jones"
        assert hn.suffix == "jr."
        assert hn.nickname != ""

    @pytest.mark.xfail
    def test_nickname_and_last_name_with_title(self):
        hn = HumanName('Senator "Rick" Edmonds')
        assert hn.title == "senator"
        assert hn.first == ""
        assert hn.last == "edmonds"
        assert hn.nickname == "rick"


class TestPrefixes:
    @pytest.mark.parametrize("entry", load_bank("prefix"), ids=lambda x: make_ids(x))
    def test_json_prefix(self, entry):
        dict_entry_test(entry)


class TestSuffixes:
    @pytest.mark.parametrize("entry", load_bank("suffix"), ids=lambda x: make_ids(x))
    def test_json_suffix(self, entry):
        dict_entry_test(entry)

    @pytest.mark.xfail(
        reason="TODO: handle conjunctions in last names"
        " followed by first names clashing with suffixes"
    )
    def test_potential_suffix_that_is_also_first_name_comma_with_conjunction(self):
        hn = HumanName("De la Vina, Bart")
        assert hn.first == "bart"
        assert hn.last == "de la vina"


class TestTitle:
    @pytest.mark.parametrize("entry", load_bank("title"), ids=lambda x: make_ids(x))
    def test_json_title(self, entry):
        dict_entry_test(entry)

    @pytest.mark.xfail(reason="TODO: fix handling of U.S.")
    def test_chained_title_first_name_title_is_initials(self):
        hn = HumanName("U.S. District Judge Marc Thomas Treadwell")
        assert hn.title == "u.s. district judge"
        assert hn.first == "marc"
        assert hn.middle == "thomas"
        assert hn.last == "treadwell"

    @pytest.mark.xfail(
        reason=" 'ben' is removed from PREFIXES in v0.2.5"
        "this test could re-enable this test if we decide to support 'ben' as a prefix"
    )
    def test_title_multiple_titles_with_apostrophe_s(self):
        hn = HumanName("The Right Hon. the President of the Queen's Bench Division")
        assert hn.title == "the right hon. the president of the queen's bench division"

    @pytest.mark.xfail
    def test_ben_as_conjunction(self):
        hn = HumanName("Ahmad ben Husain")
        assert hn.first == "ahmad"
        assert hn.last == "ben husain"


class TestHumanNameVariations:
    """Test automated variations of names in TEST_NAMES.

    Helps test that the 3 code trees work the same"""

    @pytest.mark.parametrize("name", load_bank("bare_names"))
    def test_json_variations(self, name):
        self.run_variations(name)

    def run_variations(self, name):
        """ Run several variations

        This is a separate function so that individual non-parametrized tests can be
        added if desired.
        """
        hn = HumanName(name)
        if len(hn.suffix_list) > 1:
            hn = HumanName(
                "{title} {first} {middle} {last} {suffix}".format(**hn.as_dict()).split(
                    ","
                )[0]
            )
        hn_dict = hn.as_dict()
        nocomma = HumanName(
            "{title} {first} {middle} {last} {suffix}".format(**hn_dict)
        )
        lastnamecomma = HumanName(
            "{last}, {title} {first} {middle} {suffix}".format(**hn_dict)
        )
        if hn.suffix:
            suffixcomma = HumanName(
                "{title} {first} {middle} {last}, {suffix}".format(**hn_dict)
            )
        if hn.nickname:
            nocomma = HumanName(
                "{title} {first} {middle} {last} {suffix} ({nickname})".format(
                    **hn_dict
                )
            )
            lastnamecomma = HumanName(
                "{last}, {title} {first} {middle} {suffix} ({nickname})".format(
                    **hn_dict
                )
            )
            if hn.suffix:
                suffixcomma = HumanName(
                    "{title} {first} {middle} {last}, {suffix} ({nickname})".format(
                        **hn_dict
                    )
                )
        for attr in hn._members:
            assert getattr(hn, attr) == getattr(nocomma, attr)
            assert getattr(hn, attr) == getattr(lastnamecomma, attr)
            if hn.suffix:
                assert getattr(hn, attr) == getattr(suffixcomma, attr)


class TestMaidenName:

    no_maiden_names = getattr(HumanName(), "maiden", None) is None

    @pytest.mark.skipif(no_maiden_names, reason="Maiden names not implemented.")
    def test_parenthesis_and_quotes_together(self):
        hn = HumanName("Jennifer 'Jen' Jones (Duff)")
        assert hn.first == "jennifer"
        assert hn.last == "jones"
        assert hn.nickname == "jen"
        assert hn.maiden == "duff"

    @pytest.mark.skipif(no_maiden_names, reason="Maiden names not implemented.")
    def test_maiden_name_with_nee(self):
        # https://en.wiktionary.org/wiki/née
        hn = HumanName("Mary Toogood nee Johnson")
        assert hn.first == "mary"
        assert hn.last == "toogood"
        assert hn.maiden == "johnson"

    @pytest.mark.skipif(no_maiden_names, reason="Maiden names not implemented.")
    def test_maiden_name_with_accented_nee(self):
        # https://en.wiktionary.org/wiki/née
        hn = HumanName("Mary Toogood née Johnson")
        assert hn.first == "mary"
        assert hn.last == "toogood"
        assert hn.maiden == "johnson"

    @pytest.mark.skipif(no_maiden_names, reason="Maiden names not implemented.")
    def test_maiden_name_with_nee_and_comma(self):
        # https://en.wiktionary.org/wiki/née
        hn = HumanName("Mary Toogood, née Johnson")
        assert hn.first == "mary"
        assert hn.last == "toogood"
        assert hn.maiden == "johnson"

    @pytest.mark.skipif(no_maiden_names, reason="Maiden names not implemented.")
    def test_maiden_name_with_nee_with_parenthesis(self):
        hn = HumanName("Mary Toogood (nee Johnson)")
        assert hn.first == "mary"
        assert hn.last == "toogood"
        assert hn.maiden == "johnson"

    @pytest.mark.skipif(no_maiden_names, reason="Maiden names not implemented.")
    def test_maiden_name_with_parenthesis(self):
        hn = HumanName("Mary Toogood (Johnson)")
        assert hn.first == "mary"
        assert hn.last == "toogood"
        assert hn.maiden == "johnson"


if __name__ == "__main__":
    import sys

    # Pass through any/all arguments to pytest
    pytest.main(sys.argv)
