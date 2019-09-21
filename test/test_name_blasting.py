import pytest

from nominally import Name

from .conftest import dict_entry_test, load_bank, make_ids


@pytest.mark.parametrize("entry", load_bank("*"), ids=make_ids)
def test_all_name_banks(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize("entry", load_bank("*"), ids=make_ids)
def test_idempotence(entry):
    name = Name(entry["raw"])
    namename = Name(str(name))
    assert name == namename


@pytest.mark.parametrize("entry", load_bank("*"), ids=make_ids)
def issue_30_check_fingerprint(entry):
    name = Name(entry["raw"])
    rawish = name._pre_clean(entry["raw"])
    if "junior" in rawish:
        return
    assert fingerprint(rawish) == fingerprint(str(name))


def fingerprint(s):
    return "".join(sorted(x for x in s if x.isalpha()))
