"""pytest ./pytest/"""

import pytest

from nominally import Name

from .conftest import load_bank, make_ids, dict_entry_test


@pytest.mark.parametrize("entry", load_bank("*"), ids=make_ids)
def test_all_name_banks(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize("entry", load_bank("*"), ids=make_ids)
def test_idempotence(entry):
    name = Name(entry["raw"])
    assert Name(name) == name
    assert Name(Name(name)) == name


class TestNameVariations:
    """Test automated variations of raw names in the 'brute_force' bank.

    Helps test that the 3 code trees work the same"""

    @pytest.mark.parametrize("name", load_bank("*"), ids=make_ids)
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
