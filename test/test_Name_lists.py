"""pytest ./pytest/"""

import pytest

from nominally import Name

from .conftest import load_bank, make_ids, dict_entry_test


class TestNameBruteForce:
    @pytest.mark.parametrize("entry", load_bank("brute_force"), ids=make_ids)
    def test_brute(self, entry):
        dict_entry_test(Name, entry)


class TestShortNames:
    @pytest.mark.parametrize("entry", load_bank("too_short"), ids=make_ids)
    def test_json_first_name(self, entry):
        dict_entry_test(Name, entry)


class TestNameConjunction:
    @pytest.mark.parametrize("entry", load_bank("conjunction"), ids=make_ids)
    def test_json_conjunction(self, entry):
        dict_entry_test(Name, entry)


class TestNickname:
    @pytest.mark.parametrize("entry", load_bank("nickname"), ids=make_ids)
    def test_json_nickname(self, entry):
        dict_entry_test(Name, entry)

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
        dict_entry_test(Name, entry)


class TestSuffixes:
    @pytest.mark.parametrize("entry", load_bank("suffix"), ids=make_ids)
    def test_json_suffix(self, entry):
        dict_entry_test(Name, entry)


class TestTitle:
    @pytest.mark.parametrize("entry", load_bank("title"), ids=make_ids)
    def test_json_title(self, entry):
        dict_entry_test(Name, entry)


class TestNameVariations:
    """Test automated variations of raw names in the 'brute_force' bank.

    Helps test that the 3 code trees work the same"""

    @pytest.mark.parametrize("name", load_bank("brute_force"), ids=make_ids)
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
            assert n[key] == nocomma[key] == lastnamecomma[key]
            if n.suffix:
                assert n[key] == suffixcomma[key]
