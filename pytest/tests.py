# -*- coding: utf-8 -*-
"""pytest ./pytest/"""

import json
import sys
from pathlib import Path

import pytest

from nameparser import HumanName
from nameparser.config import Constants, CONSTANTS
from nameparser.util import u

# // "Magistrate Judge Joaquin V.E. Manibusan, Jr", Intials seem to mess this up
# // # "Judge Callie V. S. Granade",


test_bank_file = Path(__file__).parent / "test_cases.json"
TEST_BANK = json.loads(test_bank_file.read_text())


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
        # assert hn[1:] == [
        #     "John",
        #     "P.",
        #     "Doe-Ray",
        #     "CLU, CFP, LUTC",
        #     hn.C.empty_attribute_default,
        # ]
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
        assert hn.first == ""
        assert hn.last == ""

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


class TestFirstNameHandling:
    def test_first_name(self):
        hn = HumanName("Andrew")
        assert hn.first == "Andrew"

    def test_assume_title_and_one_other_name_is_last_name(self):
        hn = HumanName("Rev Andrews")
        assert hn.title == "Rev"
        assert hn.last == "Andrews"

    # TODO: Seems "Andrews, M.D.", Andrews should be treated as a last name
    # but other suffixes like "George Jr." should be first names. Might be
    # related to https://github.com/derek73/python-nameparser/issues/2
    @pytest.mark.xfail
    def test_assume_suffix_title_and_one_other_name_is_last_name(self):
        hn = HumanName("Andrews, M.D.")
        assert hn.suffix == "M.D."
        assert hn.last == "Andrews"

    def test_suffix_in_lastname_part_of_lastname_comma_format(self):
        hn = HumanName("Smith Jr., John")
        assert hn.last == "Smith"
        assert hn.first == "John"
        assert hn.suffix == "Jr."

    def test_sir_exception_to_first_name_rule(self):
        hn = HumanName("Sir Gerald")
        assert hn.title == "Sir"
        assert hn.first == "Gerald"

    def test_king_exception_to_first_name_rule(self):
        hn = HumanName("King Henry")
        assert hn.title == "King"
        assert hn.first == "Henry"

    def test_queen_exception_to_first_name_rule(self):
        hn = HumanName("Queen Elizabeth")
        assert hn.title == "Queen"
        assert hn.first == "Elizabeth"

    def test_dame_exception_to_first_name_rule(self):
        hn = HumanName("Dame Mary")
        assert hn.title == "Dame"
        assert hn.first == "Mary"

    def test_first_name_is_not_prefix_if_only_two_parts(self):
        """When there are only two parts, don't join prefixes or conjunctions"""
        hn = HumanName("Van Nguyen")
        assert hn.first == "Van"
        assert hn.last == "Nguyen"

    def test_first_name_is_not_prefix_if_only_two_parts_comma(self):
        hn = HumanName("Nguyen, Van")
        assert hn.first == "Van"
        assert hn.last == "Nguyen"

    @pytest.mark.xfail
    def test_first_name_is_prefix_if_three_parts(self):
        """Not sure how to fix this without breaking Mr and Mrs"""
        hn = HumanName("Mr. Van Nguyen")
        assert hn.first == "Van"
        assert hn.last == "Nguyen"


class TestHumanNameBruteForce:
    @pytest.mark.parametrize("entry", TEST_BANK["brute_force"])
    # This fixes a bug in test115, which is not testing the suffix
    def test_brute(self, entry):
        hn = HumanName(entry["raw"])
        assert hn
        for attr in hn._members:
            expected = getattr(hn, attr)
            actual = entry.get(attr, CONSTANTS.empty_attribute_default)
            assert actual == expected


class TestHumanNameConjunction:
    # Last name with conjunction
    def test_last_name_with_conjunction(self):
        hn = HumanName("Jose Aznar y Lopez")
        assert hn.first == "Jose"
        assert hn.last == "Aznar y Lopez"

    def test_multiple_conjunctions(self):
        hn = HumanName("part1 of The part2 of the part3 and part4")
        assert hn.first == "part1 of The part2 of the part3 and part4"

    def test_multiple_conjunctions2(self):
        hn = HumanName("part1 of and The part2 of the part3 And part4")
        assert hn.first == "part1 of and The part2 of the part3 And part4"

    def test_ends_with_conjunction(self):
        hn = HumanName("Jon Dough and")
        assert hn.first == "Jon"
        assert hn.last == "Dough and"

    def test_ends_with_two_conjunctions(self):
        hn = HumanName("Jon Dough and of")
        assert hn.first == "Jon"
        assert hn.last == "Dough and of"

    def test_starts_with_conjunction(self):
        hn = HumanName("and Jon Dough")
        assert hn.first == "and Jon"
        assert hn.last == "Dough"

    def test_starts_with_two_conjunctions(self):
        hn = HumanName("the and Jon Dough")
        assert hn.first == "the and Jon"
        assert hn.last == "Dough"

    # Potential conjunction/prefix treated as initial (because uppercase)
    def test_uppercase_middle_initial_conflict_with_conjunction(self):
        hn = HumanName("John E Smith")
        assert hn.first == "John"
        assert hn.middle == "E"
        assert hn.last == "Smith"

    def test_lowercase_middle_initial_with_period_conflict_with_conjunction(self):
        hn = HumanName("john e. smith")
        assert hn.first == "john"
        assert hn.middle == "e."
        assert hn.last == "smith"

    # The conjunction "e" can also be an initial
    def test_lowercase_first_initial_conflict_with_conjunction(self):
        hn = HumanName("e j smith")
        assert hn.first == "e"
        assert hn.middle == "j"
        assert hn.last == "smith"

    def test_lowercase_middle_initial_conflict_with_conjunction(self):
        hn = HumanName("John e Smith")
        assert hn.first == "John"
        assert hn.middle == "e"
        assert hn.last == "Smith"

    def test_lowercase_middle_initial_and_suffix_conflict_with_conjunction(self):
        hn = HumanName("John e Smith, III")
        assert hn.first == "John"
        assert hn.middle == "e"
        assert hn.last == "Smith"
        assert hn.suffix == "III"

    def test_lowercase_middle_initial_and_nocomma_suffix_conflict_with_conjunction(
        self
    ):
        hn = HumanName("John e Smith III")
        assert hn.first == "John"
        assert hn.middle == "e"
        assert hn.last == "Smith"
        assert hn.suffix == "III"

    def test_lowercase_middle_initial_comma_lastname_and_suffix_conflict_with_conjunction(
        self
    ):
        hn = HumanName("Smith, John e, III, Jr")
        assert hn.first == "John"
        assert hn.middle == "e"
        assert hn.last == "Smith"
        assert hn.suffix == "III, Jr"

    @pytest.mark.xfail
    def test_two_initials_conflict_with_conjunction(self):
        # Supporting this seems to screw up titles with periods in them like M.B.A.
        hn = HumanName("E.T. Smith")
        assert hn.first == "E."
        assert hn.middle == "T."
        assert hn.last == "Smith"

    def test_couples_names(self):
        hn = HumanName("John and Jane Smith")
        assert hn.first == "John and Jane"
        assert hn.last == "Smith"

    def test_couples_names_with_conjunction_lastname(self):
        hn = HumanName("John and Jane Aznar y Lopez")
        assert hn.first == "John and Jane"
        assert hn.last == "Aznar y Lopez"

    def test_couple_titles(self):
        hn = HumanName("Mr. and Mrs. John and Jane Smith")
        assert hn.title == "Mr. and Mrs."
        assert hn.first == "John and Jane"
        assert hn.last == "Smith"

    def test_title_with_three_part_name_last_initial_is_suffix_uppercase_no_period(
        self
    ):
        hn = HumanName("King John Alexander V")
        assert hn.title == "King"
        assert hn.first == "John"
        assert hn.last == "Alexander"
        assert hn.suffix == "V"

    def test_four_name_parts_with_suffix_that_could_be_initial_lowercase_no_period(
        self
    ):
        hn = HumanName("larry james edward johnson v")
        assert hn.first == "larry"
        assert hn.middle == "james edward"
        assert hn.last == "johnson"
        assert hn.suffix == "v"

    def test_four_name_parts_with_suffix_that_could_be_initial_uppercase_no_period(
        self
    ):
        hn = HumanName("Larry James Johnson I")
        assert hn.first == "Larry"
        assert hn.middle == "James"
        assert hn.last == "Johnson"
        assert hn.suffix == "I"

    def test_roman_numeral_initials(self):
        hn = HumanName("Larry V I")
        assert hn.first == "Larry"
        assert hn.middle == "V"
        assert hn.last == "I"
        assert hn.suffix == ""

    # tests for Rev. title (Reverend)
    def test124(self):
        hn = HumanName("Rev. John A. Kenneth Doe")
        assert hn.title == "Rev."
        assert hn.middle == "A. Kenneth"
        assert hn.first == "John"
        assert hn.last == "Doe"

    def test125(self):
        hn = HumanName("Rev John A. Kenneth Doe")
        assert hn.title == "Rev"
        assert hn.middle == "A. Kenneth"
        assert hn.first == "John"
        assert hn.last == "Doe"

    def test126(self):
        hn = HumanName("Doe, Rev. John A. Jr.")
        assert hn.title == "Rev."
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.middle == "A."
        assert hn.suffix == "Jr."

    def test127(self):
        hn = HumanName("Buca di Beppo")
        assert hn.first == "Buca"
        assert hn.last == "di Beppo"

    def test_le_as_last_name(self):
        hn = HumanName("Yin Le")
        assert hn.first == "Yin"
        assert hn.last == "Le"

    def test_le_as_last_name_with_middle_initial(self):
        hn = HumanName("Yin a Le")
        assert hn.first == "Yin"
        assert hn.middle == "a"
        assert hn.last == "Le"

    def test_conjunction_in_an_address_with_a_title(self):
        hn = HumanName("His Excellency Lord Duncan")
        assert hn.title == "His Excellency Lord"
        assert hn.last == "Duncan"

    @pytest.mark.xfail
    def test_conjunction_in_an_address_with_a_first_name_title(self):
        hn = HumanName("Her Majesty Queen Elizabeth")
        assert hn.title == "Her Majesty Queen"
        # if you want to be technical, Queen is in FIRST_NAME_TITLES
        assert hn.first == "Elizabeth"

    def test_name_is_conjunctions(self):
        hn = HumanName("e and e")
        assert hn.first == "e and e"


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
    # https://code.google.com/p/python-nameparser/issues/detail?id=33
    def test_nickname_in_parenthesis(self):
        hn = HumanName("Benjamin (Ben) Franklin")
        assert hn.first == "Benjamin"
        assert hn.middle == ""
        assert hn.last == "Franklin"
        assert hn.nickname == "Ben"

    def test_two_word_nickname_in_parenthesis(self):
        hn = HumanName("Benjamin (Big Ben) Franklin")
        assert hn.first == "Benjamin"
        assert hn.middle == ""
        assert hn.last == "Franklin"
        assert hn.nickname == "Big Ben"

    def test_two_words_in_quotes(self):
        hn = HumanName('Benjamin "Big Ben" Franklin')
        assert hn.first == "Benjamin"
        assert hn.middle == ""
        assert hn.last == "Franklin"
        assert hn.nickname == "Big Ben"

    def test_nickname_in_parenthesis_with_comma(self):
        hn = HumanName("Franklin, Benjamin (Ben)")
        assert hn.first == "Benjamin"
        assert hn.middle == ""
        assert hn.last == "Franklin"
        assert hn.nickname == "Ben"

    def test_nickname_in_parenthesis_with_comma_and_suffix(self):
        hn = HumanName("Franklin, Benjamin (Ben), Jr.")
        assert hn.first == "Benjamin"
        assert hn.middle == ""
        assert hn.last == "Franklin"
        assert hn.suffix == "Jr."
        assert hn.nickname == "Ben"

    def test_nickname_in_single_quotes(self):
        hn = HumanName("Benjamin 'Ben' Franklin")
        assert hn.first == "Benjamin"
        assert hn.middle == ""
        assert hn.last == "Franklin"
        assert hn.nickname == "Ben"

    def test_nickname_in_double_quotes(self):
        hn = HumanName('Benjamin "Ben" Franklin')
        assert hn.first == "Benjamin"
        assert hn.middle == ""
        assert hn.last == "Franklin"
        assert hn.nickname == "Ben"

    def test_single_quotes_on_first_name_not_treated_as_nickname(self):
        hn = HumanName("Brian Andrew O'connor")
        assert hn.first == "Brian"
        assert hn.middle == "Andrew"
        assert hn.last == "O'connor"
        assert hn.nickname == ""

    def test_single_quotes_on_both_name_not_treated_as_nickname(self):
        hn = HumanName("La'tanya O'connor")
        assert hn.first == "La'tanya"
        assert hn.middle == ""
        assert hn.last == "O'connor"
        assert hn.nickname == ""

    def test_single_quotes_on_end_of_last_name_not_treated_as_nickname(self):
        hn = HumanName("Mari' Aube'")
        assert hn.first == "Mari'"
        assert hn.middle == ""
        assert hn.last == "Aube'"
        assert hn.nickname == ""

    def test_okina_inside_name_not_treated_as_nickname(self):
        hn = HumanName("Harrieta Keōpūolani Nāhiʻenaʻena")
        assert hn.first == "Harrieta"
        assert hn.middle == "Keōpūolani"
        assert hn.last == "Nāhiʻenaʻena"
        assert hn.nickname == ""

    def test_single_quotes_not_treated_as_nickname_Hawaiian_example(self):
        hn = HumanName("Harietta Keopuolani Nahi'ena'ena")
        assert hn.first == "Harietta"
        assert hn.middle == "Keopuolani"
        assert hn.last == "Nahi'ena'ena"
        assert hn.nickname == ""

    def test_single_quotes_not_treated_as_nickname_Kenyan_example(self):
        hn = HumanName("Naomi Wambui Ng'ang'a")
        assert hn.first == "Naomi"
        assert hn.middle == "Wambui"
        assert hn.last == "Ng'ang'a"
        assert hn.nickname == ""

    def test_single_quotes_not_treated_as_nickname_Samoan_example(self):
        hn = HumanName("Va'apu'u Vitale")
        assert hn.first == "Va'apu'u"
        assert hn.middle == ""
        assert hn.last == "Vitale"
        assert hn.nickname == ""

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

    def test_nickname_and_last_name(self):
        hn = HumanName('"Rick" Edmonds')
        assert hn.first == ""
        assert hn.last == "Edmonds"
        assert hn.nickname == "Rick"

    @pytest.mark.xfail
    def test_nickname_and_last_name_with_title(self):
        hn = HumanName('Senator "Rick" Edmonds')
        assert hn.title == "Senator"
        assert hn.first == ""
        assert hn.last == "Edmonds"
        assert hn.nickname == "Rick"


class TestPrefixes:
    def test_prefix(self):
        hn = HumanName("Juan del Sur")
        assert hn.first == "Juan"
        assert hn.last == "del Sur"

    def test_prefix_with_period(self):
        hn = HumanName("Jill St. John")
        assert hn.first == "Jill"
        assert hn.last == "St. John"

    def test_prefix_before_two_part_last_name(self):
        hn = HumanName("pennie von bergen wessels")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"

    def test_prefix_before_two_part_last_name_with_suffix(self):
        hn = HumanName("pennie von bergen wessels III")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"
        assert hn.suffix == "III"

    def test_prefix_before_two_part_last_name_with_acronym_suffix(self):
        hn = HumanName("pennie von bergen wessels M.D.")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"
        assert hn.suffix == "M.D."

    def test_two_part_last_name_with_suffix_comma(self):
        hn = HumanName("pennie von bergen wessels, III")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"
        assert hn.suffix == "III"

    def test_two_part_last_name_with_suffix(self):
        hn = HumanName("von bergen wessels, pennie III")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"
        assert hn.suffix == "III"

    def test_last_name_two_part_last_name_with_two_suffixes(self):
        hn = HumanName("von bergen wessels MD, pennie III")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"
        assert hn.suffix == "MD, III"

    def test_comma_two_part_last_name_with_acronym_suffix(self):
        hn = HumanName("von bergen wessels, pennie MD")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"
        assert hn.suffix == "MD"

    def test_comma_two_part_last_name_with_suffix_in_first_part(self):
        # I'm kinda surprised this works, not really sure if this is a
        # realistic place for a suffix to be.
        hn = HumanName("von bergen wessels MD, pennie")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"
        assert hn.suffix == "MD"

    def test_title_two_part_last_name_with_suffix_in_first_part(self):
        hn = HumanName("pennie von bergen wessels MD, III")
        assert hn.first == "pennie"
        assert hn.last == "von bergen wessels"
        assert hn.suffix == "MD, III"

    def test_portuguese_dos(self):
        hn = HumanName("Rafael Sousa dos Anjos")
        assert hn.first == "Rafael"
        assert hn.middle == "Sousa"
        assert hn.last == "dos Anjos"

    def test_portuguese_prefixes(self):
        hn = HumanName("Joao da Silva do Amaral de Souza")
        assert hn.first == "Joao"
        assert hn.middle == "da Silva do Amaral"
        assert hn.last == "de Souza"

    def test_three_conjunctions(self):
        hn = HumanName("Dr. Juan Q. Xavier de la dos Vega III")
        assert hn.first == "Juan"
        assert hn.last == "de la dos Vega"
        assert hn.title == "Dr."
        assert hn.middle == "Q. Xavier"
        assert hn.suffix == "III"

    def test_lastname_three_conjunctions(self):
        hn = HumanName("de la dos Vega, Dr. Juan Q. Xavier III")
        assert hn.first == "Juan"
        assert hn.last == "de la dos Vega"
        assert hn.title == "Dr."
        assert hn.middle == "Q. Xavier"
        assert hn.suffix == "III"

    def test_comma_three_conjunctions(self):
        hn = HumanName("Dr. Juan Q. Xavier de la dos Vega, III")
        assert hn.first == "Juan"
        assert hn.last == "de la dos Vega"
        assert hn.title == "Dr."
        assert hn.middle == "Q. Xavier"
        assert hn.suffix == "III"


class TestSuffixes:
    def test_suffix(self):
        hn = HumanName("Joe Franklin Jr")
        assert hn.first == "Joe"
        assert hn.last == "Franklin"
        assert hn.suffix == "Jr"

    def test_suffix_with_periods(self):
        hn = HumanName("Joe Dentist D.D.S.")
        assert hn.first == "Joe"
        assert hn.last == "Dentist"
        assert hn.suffix == "D.D.S."

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

    def test_two_suffixes_suffix_comma_format(self):
        hn = HumanName("Franklin Washington, Jr. MD")
        assert hn.first == "Franklin"
        assert hn.last == "Washington"
        assert hn.suffix == "Jr. MD"

    def test_suffix_containing_periods(self):
        hn = HumanName("Kenneth Clarke Q.C.")
        assert hn.first == "Kenneth"
        assert hn.last == "Clarke"
        assert hn.suffix == "Q.C."

    def test_suffix_containing_periods_lastname_comma_format(self):
        hn = HumanName("Clarke, Kenneth, Q.C. M.P.")
        assert hn.first == "Kenneth"
        assert hn.last == "Clarke"
        assert hn.suffix == "Q.C. M.P."

    def test_suffix_containing_periods_suffix_comma_format(self):
        hn = HumanName("Kenneth Clarke Q.C., M.P.")
        assert hn.first == "Kenneth"
        assert hn.last == "Clarke"
        assert hn.suffix == "Q.C., M.P."

    def test_suffix_with_single_comma_format(self):
        hn = HumanName("John Doe jr., MD")
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.suffix == "jr., MD"

    def test_suffix_with_double_comma_format(self):
        hn = HumanName("Doe, John jr., MD")
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.suffix == "jr., MD"

    def test_phd_with_erroneous_space(self):
        hn = HumanName("John Smith, Ph. D.")
        assert hn.first == "John"
        assert hn.last == "Smith"
        assert hn.suffix == "Ph. D."

    def test_phd_conflict(self):
        hn = HumanName("Adolph D")
        assert hn.first == "Adolph"
        assert hn.last == "D"

    # http://en.wikipedia.org/wiki/Ma_(surname)
    def test_potential_suffix_that_is_also_last_name(self):
        hn = HumanName("Jack Ma")
        assert hn.first == "Jack"
        assert hn.last == "Ma"

    def test_potential_suffix_that_is_also_last_name_comma(self):
        hn = HumanName("Ma, Jack")
        assert hn.first == "Jack"
        assert hn.last == "Ma"

    def test_potential_suffix_that_is_also_first_name_comma(self):
        hn = HumanName("Johnson, Bart")
        assert hn.first == "Bart"
        assert hn.last == "Johnson"

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

    def test_multiple_letter_suffix_with_periods(self):
        hn = HumanName("John Doe Msc.Ed.")
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.suffix == "Msc.Ed."

    def test_suffix_with_periods_with_comma(self):
        hn = HumanName("John Doe, Msc.Ed.")
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.suffix == "Msc.Ed."

    def test_suffix_with_periods_with_lastname_comma(self):
        hn = HumanName("Doe, John Msc.Ed.")
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.suffix == "Msc.Ed."


class TestTitle:
    def test_last_name_is_also_title(self):
        hn = HumanName("Amy E Maid")
        assert hn.first == "Amy"
        assert hn.middle == "E"
        assert hn.last == "Maid"

    def test_last_name_is_also_title_no_comma(self):
        hn = HumanName("Dr. Martin Luther King Jr.")
        assert hn.title == "Dr."
        assert hn.first == "Martin"
        assert hn.middle == "Luther"
        assert hn.last == "King"
        assert hn.suffix == "Jr."

    def test_last_name_is_also_title_with_comma(self):
        hn = HumanName("Duke Martin Luther King, Jr.")
        assert hn.title == "Duke"
        assert hn.first == "Martin"
        assert hn.middle == "Luther"
        assert hn.last == "King"
        assert hn.suffix == "Jr."

    def test_last_name_is_also_title3(self):
        hn = HumanName("John King")
        assert hn.first == "John"
        assert hn.last == "King"

    def test_title_with_conjunction(self):
        hn = HumanName("Secretary of State Hillary Clinton")
        assert hn.title == "Secretary of State"
        assert hn.first == "Hillary"
        assert hn.last == "Clinton"

    def test_compound_title_with_conjunction(self):
        hn = HumanName("Cardinal Secretary of State Hillary Clinton")
        assert hn.title == "Cardinal Secretary of State"
        assert hn.first == "Hillary"
        assert hn.last == "Clinton"

    def test_title_is_title(self):
        hn = HumanName("Coach")
        assert hn.title == "Coach"

    # TODO: fix handling of U.S.
    @pytest.mark.xfail
    def test_chained_title_first_name_title_is_initials(self):
        hn = HumanName("U.S. District Judge Marc Thomas Treadwell")
        assert hn.title == "U.S. District Judge"
        assert hn.first == "Marc"
        assert hn.middle == "Thomas"
        assert hn.last == "Treadwell"

    def test_conflict_with_chained_title_first_name_initial(self):
        hn = HumanName("U. S. Grant")
        assert hn.first == "U."
        assert hn.middle == "S."
        assert hn.last == "Grant"

    def test_chained_title_first_name_initial_with_no_period(self):
        hn = HumanName("US Magistrate Judge T Michael Putnam")
        assert hn.title == "US Magistrate Judge"
        assert hn.first == "T"
        assert hn.middle == "Michael"
        assert hn.last == "Putnam"

    def test_chained_hyphenated_title(self):
        hn = HumanName("US Magistrate-Judge Elizabeth E Campbell")
        assert hn.title == "US Magistrate-Judge"
        assert hn.first == "Elizabeth"
        assert hn.middle == "E"
        assert hn.last == "Campbell"

    def test_chained_hyphenated_title_with_comma_suffix(self):
        hn = HumanName("Mag-Judge Harwell G Davis, III")
        assert hn.title == "Mag-Judge"
        assert hn.first == "Harwell"
        assert hn.middle == "G"
        assert hn.last == "Davis"
        assert hn.suffix == "III"

    @pytest.mark.xfail
    def test_title_multiple_titles_with_apostrophe_s(self):
        hn = HumanName("The Right Hon. the President of the Queen's Bench Division")
        self.m(
            hn.title, "The Right Hon. the President of the Queen's Bench Division", hn
        )

    def test_title_starts_with_conjunction(self):
        hn = HumanName("The Rt Hon John Jones")
        assert hn.title == "The Rt Hon"
        assert hn.first == "John"
        assert hn.last == "Jones"

    def test_conjunction_before_title(self):
        hn = HumanName("The Lord of the Universe")
        assert hn.title == "The Lord of the Universe"

    def test_double_conjunction_on_title(self):
        hn = HumanName("Lord of the Universe")
        assert hn.title == "Lord of the Universe"

    def test_triple_conjunction_on_title(self):
        hn = HumanName("Lord and of the Universe")
        assert hn.title == "Lord and of the Universe"

    def test_multiple_conjunctions_on_multiple_titles(self):
        hn = HumanName(
            "Lord of the Universe and Associate Supreme Queen of the World Lisa Simpson"
        )
        assert (
            hn.title == "Lord of the Universe and Associate Supreme Queen of the World"
        )
        assert hn.first == "Lisa"
        assert hn.last == "Simpson"

    def test_title_with_last_initial_is_suffix(self):
        hn = HumanName("King John V.")
        assert hn.title == "King"
        assert hn.first == "John"
        assert hn.last == "V."

    def test_initials_also_suffix(self):
        hn = HumanName("Smith, J.R.")
        assert hn.first == "J.R."
        # assert hn.middle == "R."
        assert hn.last == "Smith"

    def test_two_title_parts_separated_by_periods(self):
        hn = HumanName("Lt.Gen. John A. Kenneth Doe IV")
        assert hn.title == "Lt.Gen."
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.middle == "A. Kenneth"
        assert hn.suffix == "IV"

    def test_two_part_title(self):
        hn = HumanName("Lt. Gen. John A. Kenneth Doe IV")
        assert hn.title == "Lt. Gen."
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.middle == "A. Kenneth"
        assert hn.suffix == "IV"

    def test_two_part_title_with_lastname_comma(self):
        hn = HumanName("Doe, Lt. Gen. John A. Kenneth IV")
        assert hn.title == "Lt. Gen."
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.middle == "A. Kenneth"
        assert hn.suffix == "IV"

    def test_two_part_title_with_suffix_comma(self):
        hn = HumanName("Lt. Gen. John A. Kenneth Doe, Jr.")
        assert hn.title == "Lt. Gen."
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.middle == "A. Kenneth"
        assert hn.suffix == "Jr."

    def test_possible_conflict_with_middle_initial_that_could_be_suffix(self):
        hn = HumanName("Doe, Rev. John V, Jr.")
        assert hn.title == "Rev."
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.middle == "V"
        assert hn.suffix == "Jr."

    def test_possible_conflict_with_suffix_that_could_be_initial(self):
        hn = HumanName("Doe, Rev. John A., V, Jr.")
        assert hn.title == "Rev."
        assert hn.first == "John"
        assert hn.last == "Doe"
        assert hn.middle == "A."
        assert hn.suffix == "V, Jr."

    # 'ben' is removed from PREFIXES in v0.2.5
    # this test could re-enable this test if we decide to support 'ben' as a prefix
    @pytest.mark.xfail
    def test_ben_as_conjunction(self):
        hn = HumanName("Ahmad ben Husain")
        assert hn.first == "Ahmad"
        assert hn.last == "ben Husain"

    def test_ben_as_first_name(self):
        hn = HumanName("Ben Johnson")
        assert hn.first == "Ben"
        assert hn.last == "Johnson"

    def test_ben_as_first_name_with_middle_name(self):
        hn = HumanName("Ben Alex Johnson")
        assert hn.first == "Ben"
        assert hn.middle == "Alex"
        assert hn.last == "Johnson"

    def test_ben_as_middle_name(self):
        hn = HumanName("Alex Ben Johnson")
        assert hn.first == "Alex"
        assert hn.middle == "Ben"
        assert hn.last == "Johnson"

    # http://code.google.com/p/python-nameparser/issues/detail?id=13
    def test_last_name_also_prefix(self):
        hn = HumanName("Jane Doctor")
        assert hn.first == "Jane"
        assert hn.last == "Doctor"

    def test_title_with_periods(self):
        hn = HumanName("Lt.Gov. John Doe")
        assert hn.title == "Lt.Gov."
        assert hn.first == "John"
        assert hn.last == "Doe"

    def test_title_with_periods_lastname_comma(self):
        hn = HumanName("Doe, Lt.Gov. John")
        assert hn.title == "Lt.Gov."
        assert hn.first == "John"
        assert hn.last == "Doe"


class TestHumanNameCapitalization:
    def test_capitalization_exception_for_III(self):
        hn = HumanName("juan q. xavier velasquez y garcia iii")
        hn.capitalize()
        assert str(hn) == "Juan Q. Xavier Velasquez y Garcia III"

    # FIXME: this test does not pass due to a known issue
    # http://code.google.com/p/python-nameparser/issues/detail?id=22
    @pytest.mark.xfail
    def test_capitalization_exception_for_already_capitalized_III_KNOWN_FAILURE(self):
        hn = HumanName("juan garcia III")
        hn.capitalize()
        assert str(hn) == "Juan Garcia III"

    def test_capitalize_title(self):
        hn = HumanName("lt. gen. john a. kenneth doe iv")
        hn.capitalize()
        assert str(hn) == "Lt. Gen. John A. Kenneth Doe IV"

    def test_capitalize_title_to_lower(self):
        hn = HumanName("LT. GEN. JOHN A. KENNETH DOE IV")
        hn.capitalize()
        assert str(hn) == "Lt. Gen. John A. Kenneth Doe IV"

    # Capitalization with M(a)c and hyphenated names
    def test_capitalization_with_Mac_as_hyphenated_names(self):
        hn = HumanName("donovan mcnabb-smith")
        hn.capitalize()
        assert str(hn) == "Donovan McNabb-Smith"

    def test_capitization_middle_initial_is_also_a_conjunction(self):
        hn = HumanName("scott e. werner")
        hn.capitalize()
        assert str(hn) == "Scott E. Werner"

    # Leaving already-capitalized names alone
    def test_no_change_to_mixed_chase(self):
        hn = HumanName("Shirley Maclaine")
        hn.capitalize()
        assert str(hn) == "Shirley Maclaine"

    def test_force_capitalization(self):
        hn = HumanName("Shirley Maclaine")
        hn.capitalize(force=True)
        assert str(hn) == "Shirley MacLaine"

    def test_capitalize_diacritics(self):
        hn = HumanName("matthëus schmidt")
        hn.capitalize()
        assert u(hn) == "Matthëus Schmidt"

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

    def test_short_names_with_mac(self):
        hn = HumanName("mack johnson")
        hn.capitalize()
        assert str(hn) == "Mack Johnson"

    def test_portuguese_prefixes(self):
        hn = HumanName("joao da silva do amaral de souza")
        hn.capitalize()
        assert str(hn) == "Joao da Silva do Amaral de Souza"

    def test_capitalize_prefix_clash_on_first_name(self):
        hn = HumanName("van nguyen")
        hn.capitalize()
        assert str(hn) == "Van Nguyen"


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
    # test automated variations of names in TEST_NAMES.
    # Helps test that the 3 code trees work the same

    TEST_NAMES = set(
        TEST_BANK["test_names"] + [x["raw"] for x in TEST_BANK["brute_force"]]
    )

    @pytest.mark.parametrize("name", TEST_NAMES)
    def test_variations_of_TEST_NAMES(self, name):
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
    from nameparser.config import CONSTANTS

    print("Running tests")
    pytest.main([__file__])
    print("Running tests with empty_attribute_default = None")
    global CONSTANTS
    CONSTANTS.empty_attribute_default = None
    pytest.main([__file__])
