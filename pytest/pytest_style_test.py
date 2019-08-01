# -*- coding: utf-8 -*-
"""pytest ./pytest/"""

import json
import sys
from pathlib import Path

import pytest

from nameparser import HumanName
from nameparser.config import Constants, CONSTANTS
from nameparser.util import u


test_bank_file = Path(__file__).parent / "test_cases.json"
TEST_BANK = json.loads(test_bank_file.read_text(encoding="utf8"))


def dict_entry_test(dict_entry):
    hn = HumanName(dict_entry["raw"])
    for attr in hn._members:
        actual = getattr(hn, attr)
        expected = dict_entry.get(attr, CONSTANTS.empty_attribute_default)
        assert actual == expected


def make_ids(entry):
    return entry.get("id") or entry.get("raw")


class TestCoreFunctionality:
    def test_utf8(self):
        hn = HumanName("de la Véña, Jüan")
        assert hn.first == "Jüan"
        assert hn.last == "de la Véña"

    def test_string_output(self):
        hn = HumanName("de la Véña, Jüan")
        print(hn)
        print(repr(hn))

    def test_escaped_utf8_bytes(self):
        hn = HumanName(b"B\xc3\xb6ck, Gerald")
        assert hn.first == "Gerald"
        assert hn.last == "Böck"

    @pytest.mark.parametrize(
        "raw, length", [("Doe-Ray, Dr. John P., CLU, CFP, LUTC", 5), ("John Doe", 2)]
    )
    def test_len(self, raw, length):
        assert len(HumanName(raw)) == length

    def test_comparison(self):
        hn1 = HumanName("Doe-Ray, Dr. John P., CLU, CFP, LUTC")
        hn2 = HumanName("Dr. John P. Doe-Ray, CLU, CFP, LUTC")
        assert hn1 == hn2
        assert hn1 is not hn2
        assert hn1 == "Dr. John P. Doe-Ray CLU, CFP, LUTC"
        hn1 = HumanName("Doe, Dr. John P., CLU, CFP, LUTC")
        hn2 = HumanName("Dr. John P. Doe-Ray, CLU, CFP, LUTC")
        assert hn1 != hn2
        assert hn1 != 0
        assert hn1 != "test"
        assert hn1 != ["test"]
        assert hn1 != {"test": hn2}

    def test_assignment_to_full_name(self):
        hn = HumanName("John A. Kenneth Doe, Jr.")
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.middle == "A. Kenneth"
        assert hn.suffix == "Jr."
        hn.full_name = "Juan Velasquez y Garcia III"
        assert hn.first == "Juan"
        assert hn.last == "Velasquez y Garcia"
        assert hn.suffix == "III"

    def test_get_full_name_attribute_references_internal_lists(self):
        hn = HumanName("John Williams")
        hn.first_list = ["Larry"]
        assert hn.full_name, "Larry Williams"

    def test_assignment_to_attribute(self):
        hn = HumanName("John A. Kenneth Doe, Jr.")
        hn.last = "de la Vega"
        assert hn.last == "de la Vega"
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
        assert hn1 == "Dr. John P. Doe-ray clu, CFP, LUTC"

    def test_slice(self):
        hn = HumanName("Doe-Ray, Dr. John P., CLU, CFP, LUTC")
        assert list(hn), ["Dr.", "John", "P.", "Doe-Ray", "CLU, CFP, LUTC"]
        assert hn[1:] == [
            "John",
            "P.",
            "Doe-Ray",
            "CLU, CFP, LUTC",
            hn.C.empty_attribute_default,
        ]
        assert hn[1:-2], ["John", "P.", "Doe-Ray"]

    def test_getitem(self):
        hn = HumanName("Dr. John A. Kenneth Doe, Jr.")
        assert hn["title"], "Dr."
        assert hn["first"], "John"
        assert hn["last"], "Doe"
        assert hn["middle"], "A. Kenneth"
        assert hn["suffix"], "Jr."

    def test_setitem(self):
        hn = HumanName("Dr. John A. Kenneth Doe, Jr.")
        hn["title"] = "test"
        assert hn["title"], "test"
        hn["last"] = ["test", "test2"]
        assert hn["last"], "test test2"
        with pytest.raises(TypeError):
            hn["suffix"] = [["test"]]
        with pytest.raises(TypeError):
            hn["suffix"] = {"test": "test"}

    def test_conjunction_names(self):
        hn = HumanName("johnny y")
        assert hn.first == "johnny"
        assert hn.last == "y"

    def test_prefix_names(self):
        hn = HumanName("vai la")
        assert hn.first == "vai"
        assert hn.last == "la"

    def test_blank_name(self):
        hn = HumanName()
        assert hn.first == CONSTANTS.empty_attribute_default
        assert hn.last == CONSTANTS.empty_attribute_default

    def test_surnames_list_attribute(self):
        hn = HumanName("John Edgar Casey Williams III")
        assert hn.surnames_list, ["Edgar", "Casey", "Williams"]

    def test_surnames_attribute(self):
        hn = HumanName("John Edgar Casey Williams III")
        assert hn.surnames == "Edgar Casey Williams"


def test_pickle():
    dill = pytest.importorskip("dill")

    # test_config_pickle
    constants = Constants()
    dill.pickles(constants)

    # test_name_instance_pickle
    hn = HumanName("Title First Middle Middle Last, Jr.")
    dill.pickles(hn)


class TestHumanNameBruteForce:
    # This fixes a bug in test115, which is not testing the suffix
    @pytest.mark.parametrize(
        "entry", TEST_BANK["brute_force"], ids=lambda x: make_ids(x)
    )
    def test_brute(self, entry):
        dict_entry_test(entry)


class TestFirstNameHandling:
    @pytest.mark.parametrize(
        "entry", TEST_BANK["first_name"], ids=lambda x: make_ids(x)
    )
    def test_json_first_name(self, entry):
        dict_entry_test(entry)

    # TODO: Seems "Andrews, M.D.", Andrews should be treated as a last name
    # but other suffixes like "George Jr." should be first names. Might be
    # related to https://github.com/derek73/python-nameparser/issues/2
    @pytest.mark.xfail
    def test_assume_suffix_title_and_one_other_name_is_last_name(self):
        hn = HumanName("Andrews, M.D.")
        assert hn.suffix == "M.D."
        assert hn.last == "Andrews"

    def test_first_name_is_not_prefix_if_only_two_parts(self):
        """When there are only two parts, don't join prefixes or conjunctions"""
        hn = HumanName("Van Nguyen")
        assert hn.first == "Van"
        assert hn.last == "Nguyen"

    @pytest.mark.xfail
    def test_first_name_is_prefix_if_three_parts(self):
        """Not sure how to fix this without breaking Mr and Mrs"""
        hn = HumanName("Mr. Van Nguyen")
        assert hn.first == "Van"
        assert hn.last == "Nguyen"


class TestHumanNameConjunction:
    @pytest.mark.parametrize(
        "entry", TEST_BANK["conjunction"], ids=lambda x: make_ids(x)
    )
    def test_json_conjunction(self, entry):
        dict_entry_test(entry)

    @pytest.mark.xfail
    def test_two_initials_conflict_with_conjunction(self):
        # Supporting this seems to screw up titles with periods in them like M.B.A.
        hn = HumanName("E.T. Smith")
        assert hn.first == "E."
        assert hn.middle == "T."
        assert hn.last == "Smith"

    @pytest.mark.xfail
    def test_conjunction_in_an_address_with_a_first_name_title(self):
        hn = HumanName("Her Majesty Queen Elizabeth")
        assert hn.title == "Her Majesty Queen"
        # if you want to be technical, Queen is in FIRST_NAME_TITLES
        assert hn.first == "Elizabeth"


class TestConstantsCustomization:
    def test_add_title(self):
        hn = HumanName("Te Awanui-a-Rangi Black", constants=None)
        start_len = len(hn.C.titles)
        assert start_len > 0
        hn.C.titles.add("te")
        assert start_len + 1 == len(hn.C.titles)
        hn.parse_full_name()
        assert hn.title == "Te"
        assert hn.first == "Awanui-a-Rangi"
        assert hn.last == "Black"

    def test_remove_title(self):
        hn = HumanName("Hon Solo", constants=None)
        start_len = len(hn.C.titles)
        assert start_len > 0
        hn.C.titles.remove("hon")
        assert start_len - 1 == len(hn.C.titles)
        hn.parse_full_name()
        assert hn.first == "Hon"
        assert hn.last == "Solo"

    def test_add_multiple_arguments(self):
        hn = HumanName("Assoc Dean of Chemistry Robert Johns", constants=None)
        hn.C.titles.add("dean", "Chemistry")
        hn.parse_full_name()
        assert hn.title == "Assoc Dean of Chemistry"
        assert hn.first == "Robert"
        assert hn.last == "Johns"

    def test_instances_can_have_own_constants(self):
        hn = HumanName("", None)
        hn2 = HumanName("")
        hn.C.titles.remove("hon")
        assert "hon" not in hn.C.titles
        assert hn.has_own_config
        assert "hon" in hn2.C.titles
        assert not hn2.has_own_config

    def test_can_change_global_constants(self):
        hn = HumanName("")
        hn2 = HumanName("")
        hn.C.titles.remove("hon")
        assert "hon" not in hn.C.titles
        assert "hon" not in hn2.C.titles
        assert not hn.has_own_config
        assert not hn2.has_own_config
        # clean up so we don't mess up other tests
        hn.C.titles.add("hon")

    def test_remove_multiple_arguments(self):
        hn = HumanName("Ms Hon Solo", constants=None)
        hn.C.titles.remove("hon", "ms")
        hn.parse_full_name()
        assert hn.first == "Ms"
        assert hn.middle == "Hon"
        assert hn.last == "Solo"

    def test_chain_multiple_arguments(self):
        hn = HumanName("Dean Ms Hon Solo", constants=None)
        hn.C.titles.remove("hon", "ms").add("dean")
        hn.parse_full_name()
        assert hn.title == "Dean"
        assert hn.first == "Ms"
        assert hn.middle == "Hon"
        assert hn.last == "Solo"

    def test_empty_attribute_default(self):
        from nameparser.config import CONSTANTS

        _orig = CONSTANTS.empty_attribute_default
        CONSTANTS.empty_attribute_default = None
        hn = HumanName("")
        assert hn.title is None
        assert hn.first is None
        assert hn.middle is None
        assert hn.last is None
        assert hn.suffix is None
        assert hn.nickname is None
        CONSTANTS.empty_attribute_default = _orig

    def test_empty_attribute_on_instance(self):
        hn = HumanName("", None)
        hn.C.empty_attribute_default = None
        assert hn.title is None
        assert hn.first is None
        assert hn.middle is None
        assert hn.last is None
        assert hn.suffix is None
        assert hn.nickname is None

    def test_none_empty_attribute_string_formatting(self):
        hn = HumanName("", None)
        hn.C.empty_attribute_default = None
        assert str(hn) == ""

    def test_add_constant_with_explicit_encoding(self):
        c = Constants()
        c.titles.add_with_encoding(b"b\351ck", encoding="latin_1")
        assert "béck" in c.titles


class TestNickname:
    @pytest.mark.parametrize("entry", TEST_BANK["nickname"], ids=lambda x: make_ids(x))
    def test_json_nickname(self, entry):
        dict_entry_test(entry)

    # https://code.google.com/p/python-nameparser/issues/detail?id=33
    def test_nickname_in_parenthesis(self):
        hn = HumanName("Benjamin (Ben) Franklin")
        assert hn.first == "Benjamin"
        assert hn.middle == CONSTANTS.empty_attribute_default
        assert hn.last == "Franklin"
        assert hn.nickname == "Ben"

    # http://code.google.com/p/python-nameparser/issues/detail?id=17
    def test_parenthesis_are_removed_from_name(self):
        hn = HumanName("John Jones (Unknown)")
        assert hn.first == "John"
        assert hn.last == "Jones"
        # not testing the nicknames because we don't actually care
        # about Google Docs here

    def test_duplicate_parenthesis_are_removed_from_name(self):
        hn = HumanName("John Jones (Google Docs), Jr. (Unknown)")
        assert hn.first == "John"
        assert hn.last == "Jones"
        assert hn.suffix == "Jr."

    @pytest.mark.xfail
    def test_nickname_and_last_name_with_title(self):
        hn = HumanName('Senator "Rick" Edmonds')
        assert hn.title == "Senator"
        assert hn.first == CONSTANTS.empty_attribute_default
        assert hn.last == "Edmonds"
        assert hn.nickname == "Rick"


class TestPrefixes:
    @pytest.mark.parametrize("entry", TEST_BANK["prefix"], ids=lambda x: make_ids(x))
    def test_json_prefix(self, entry):
        dict_entry_test(entry)

    def test_comma_two_part_last_name_with_suffix_in_first_part(self):
        # I'm kinda surprised this works, not really sure if this is a
        # realistic place for a suffix to be.
        hn = HumanName("von bergen wessels MD, pennie")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"
        assert hn.suffix == "MD"


class TestSuffixes:
    @pytest.mark.parametrize("entry", TEST_BANK["suffix"], ids=lambda x: make_ids(x))
    def test_json_suffix(self, entry):
        dict_entry_test(entry)

    def test_two_suffixes(self):
        hn = HumanName("Kenneth Clarke QC MP")
        assert hn.first == "Kenneth"
        assert hn.last == "Clarke"
        # NOTE: this adds a comma when the original format did not have one.
        # not ideal but at least its in the right bucket
        assert hn.suffix == "QC, MP"

    def test_two_suffixes_lastname_comma_format(self):
        hn = HumanName("Washington Jr. MD, Franklin")
        assert hn.first == "Franklin"
        assert hn.last == "Washington"
        # NOTE: this adds a comma when the original format did not have one.
        assert hn.suffix == "Jr., MD"

    # TODO: handle conjunctions in last names followed by first names clashing with suffixes
    @pytest.mark.xfail
    def test_potential_suffix_that_is_also_first_name_comma_with_conjunction(self):
        hn = HumanName("De la Vina, Bart")
        assert hn.first == "Bart"
        assert hn.last == "De la Vina"

    def test_potential_suffix_that_is_also_last_name_with_suffix(self):
        hn = HumanName("Jack Ma Jr")
        assert hn.first == "Jack"
        assert hn.last == "Ma"
        assert hn.suffix == "Jr"

    def test_potential_suffix_that_is_also_last_name_with_suffix_comma(self):
        hn = HumanName("Ma III, Jack Jr")
        assert hn.first == "Jack"
        assert hn.last == "Ma"
        assert hn.suffix == "III, Jr"

    # https://github.com/derek73/python-nameparser/issues/27
    @pytest.mark.xfail
    def test_king(self):
        hn = HumanName("Dr King Jr")
        assert hn.title == "Dr"
        assert hn.last == "King"
        assert hn.suffix == "Jr"


class TestTitle:
    @pytest.mark.parametrize("entry", TEST_BANK["title"], ids=lambda x: make_ids(x))
    def test_json_title(self, entry):
        dict_entry_test(entry)

    # TODO: fix handling of U.S.
    @pytest.mark.xfail
    def test_chained_title_first_name_title_is_initials(self):
        hn = HumanName("U.S. District Judge Marc Thomas Treadwell")
        assert hn.title == "U.S. District Judge"
        assert hn.first == "Marc"
        assert hn.middle == "Thomas"
        assert hn.last == "Treadwell"

    @pytest.mark.xfail
    def test_title_multiple_titles_with_apostrophe_s(self):
        hn = HumanName("The Right Hon. the President of the Queen's Bench Division")
        assert hn.title == "The Right Hon. the President of the Queen's Bench Division"

    def test_initials_also_suffix(self):
        hn = HumanName("Smith, J.R.")
        assert hn.first == "J.R."
        # assert hn.middle == "R."
        assert hn.last == "Smith"

    # 'ben' is removed from PREFIXES in v0.2.5
    # this test could re-enable this test if we decide to support 'ben' as a prefix
    @pytest.mark.xfail
    def test_ben_as_conjunction(self):
        hn = HumanName("Ahmad ben Husain")
        assert hn.first == "Ahmad"
        assert hn.last == "ben Husain"

    # http://code.google.com/p/python-nameparser/issues/detail?id=13
    def test_last_name_also_prefix(self):
        hn = HumanName("Jane Doctor")
        assert hn.first == "Jane"
        assert hn.last == "Doctor"


class TestHumanNameCapitalization:
    @pytest.mark.parametrize(
        "entry", TEST_BANK["capitalization"], ids=lambda x: make_ids(x)
    )
    def test_json_capitalization(self, entry):
        hn = HumanName(entry["raw"])
        hn.capitalize()
        assert str(hn) == entry["string"]

    def test_force_capitalization(self):
        hn = HumanName("Shirley Maclaine")
        hn.capitalize(force=True)
        assert str(hn) == "Shirley MacLaine"

    # FIXME: this test does not pass due to a known issue
    # http://code.google.com/p/python-nameparser/issues/detail?id=22
    @pytest.mark.xfail
    def test_capitalization_exception_for_already_capitalized_III_KNOWN_FAILURE(self):
        hn = HumanName("juan garcia III")
        hn.capitalize()
        assert str(hn) == "Juan Garcia III"

    # http://code.google.com/p/python-nameparser/issues/detail?id=15
    def test_downcasing_mac(self):
        hn = HumanName("RONALD MACDONALD")
        hn.capitalize()
        assert str(hn) == "Ronald MacDonald"

    # http://code.google.com/p/python-nameparser/issues/detail?id=23
    def test_downcasing_mc(self):
        hn = HumanName("RONALD MCDONALD")
        hn.capitalize()
        assert str(hn) == "Ronald McDonald"


class TestHumanNameOutputFormat:
    def test_formatting_init_argument(self):
        hn = HumanName("Rev John A. Kenneth Doe III (Kenny)", string_format="TEST1")
        assert u(hn) == "TEST1"

    def test_formatting_constants_attribute(self):
        from nameparser.config import CONSTANTS

        _orig = CONSTANTS.string_format
        CONSTANTS.string_format = "TEST2"
        hn = HumanName("Rev John A. Kenneth Doe III (Kenny)")
        assert u(hn) == "TEST2"
        CONSTANTS.string_format = _orig

    def test_quote_nickname_formating(self):
        hn = HumanName("Rev John A. Kenneth Doe III (Kenny)")
        hn.string_format = "{title} {first} {middle} {last} {suffix} '{nickname}'"
        assert u(hn) == "Rev John A. Kenneth Doe III 'Kenny'"
        hn.string_format = "{last}, {title} {first} {middle}, {suffix} '{nickname}'"
        assert u(hn) == "Doe, Rev John A. Kenneth, III 'Kenny'"

    def test_formating_removing_keys_from_format_string(self):
        hn = HumanName("Rev John A. Kenneth Doe III (Kenny)")
        hn.string_format = "{title} {first} {middle} {last} {suffix} '{nickname}'"
        assert u(hn) == "Rev John A. Kenneth Doe III 'Kenny'"
        hn.string_format = "{last}, {title} {first} {middle}, {suffix}"
        assert u(hn) == "Doe, Rev John A. Kenneth, III"
        hn.string_format = "{last}, {title} {first} {middle}"
        assert u(hn) == "Doe, Rev John A. Kenneth"
        hn.string_format = "{last}, {first} {middle}"
        assert u(hn) == "Doe, John A. Kenneth"
        hn.string_format = "{last}, {first}"
        assert u(hn) == "Doe, John"
        hn.string_format = "{first} {last}"
        assert u(hn) == "John Doe"

    def test_formating_removing_pieces_from_name_buckets(self):
        hn = HumanName("Rev John A. Kenneth Doe III (Kenny)")
        hn.string_format = "{title} {first} {middle} {last} {suffix} '{nickname}'"
        assert u(hn) == "Rev John A. Kenneth Doe III 'Kenny'"
        hn.string_format = "{title} {first} {middle} {last} {suffix}"
        assert u(hn) == "Rev John A. Kenneth Doe III"
        hn.middle = ""
        assert u(hn) == "Rev John Doe III"
        hn.suffix = ""
        assert u(hn) == "Rev John Doe"
        hn.title = ""
        assert u(hn) == "John Doe"

    def test_formating_of_nicknames_with_parenthesis(self):
        hn = HumanName("Rev John A. Kenneth Doe III (Kenny)")
        hn.string_format = "{title} {first} {middle} {last} {suffix} ({nickname})"
        assert u(hn) == "Rev John A. Kenneth Doe III (Kenny)"
        hn.nickname = ""
        assert u(hn) == "Rev John A. Kenneth Doe III"

    def test_formating_of_nicknames_with_single_quotes(self):
        hn = HumanName("Rev John A. Kenneth Doe III (Kenny)")
        hn.string_format = "{title} {first} {middle} {last} {suffix} '{nickname}'"
        assert u(hn) == "Rev John A. Kenneth Doe III 'Kenny'"
        hn.nickname = ""
        assert u(hn) == "Rev John A. Kenneth Doe III"

    def test_formating_of_nicknames_with_double_quotes(self):
        hn = HumanName("Rev John A. Kenneth Doe III (Kenny)")
        hn.string_format = '{title} {first} {middle} {last} {suffix} "{nickname}"'
        assert u(hn) == 'Rev John A. Kenneth Doe III "Kenny"'
        hn.nickname = ""
        assert u(hn) == "Rev John A. Kenneth Doe III"

    def test_formating_of_nicknames_in_middle(self):
        hn = HumanName("Rev John A. Kenneth Doe III (Kenny)")
        hn.string_format = "{title} {first} ({nickname}) {middle} {last} {suffix}"
        assert u(hn) == "Rev John (Kenny) A. Kenneth Doe III"
        hn.nickname = ""
        assert u(hn) == "Rev John A. Kenneth Doe III"

    def test_remove_emojis(self):
        hn = HumanName("Sam Smith 😊")
        assert hn.first == "Sam"
        assert hn.last == "Smith"
        assert u(hn) == "Sam Smith"

    def test_keep_non_emojis(self):
        hn = HumanName("∫≜⩕ Smith 😊")
        assert hn.first == "∫≜⩕"
        assert hn.last == "Smith"
        assert u(hn) == "∫≜⩕ Smith"

    def test_keep_emojis(self):
        constants = Constants()
        constants.regexes.emoji = False
        hn = HumanName("∫≜⩕ Smith😊", constants)
        assert hn.first == "∫≜⩕"
        assert hn.last == "Smith😊"
        assert u(hn) == "∫≜⩕ Smith😊"
        # test cleanup


class TestHumanNameVariations:
    """Test automated variations of names in TEST_NAMES.

    Helps test that the 3 code trees work the same"""

    @pytest.mark.parametrize("name", TEST_BANK["test_names"])
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
        # format strings below require empty string
        hn.C.empty_attribute_default = ""
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


if __name__ == "__main__":
    pytest.main([__file__])
