import pytest
from unidecode import unidecode_expect_ascii

from nominally import Name

from .conftest import dict_entry_test, load_bank, make_ids


@pytest.mark.parametrize("entry", load_bank("*"), ids=make_ids)
def test_all_name_banks(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize("entry", load_bank("*"), ids=make_ids)
def issue_30_check_fingerprint(entry):
    """
    This helps ensure that we aren't losing random name parts.
    """
    name = Name(entry["raw"])
    rawish = unidecode_expect_ascii(entry["raw"]).lower()

    string_finger = fingerprint(str(name))
    raw_finger = fingerprint(rawish)
    alt_finger = fingerprint(rawish.replace("junior", "jr"))

    assert string_finger in (raw_finger, alt_finger)


def fingerprint(s):
    return "".join(sorted(x for x in s if x.isalpha()))
