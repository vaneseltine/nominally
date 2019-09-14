import pytest

from nominally import Name

from .conftest import dict_entry_test


@pytest.mark.parametrize(
    "entry",
    [
        {
            "id": "della_as_first_name",
            "raw": "della fennel",
            "first": "della",
            "last": "fennel",
        },
        {
            "id": "della_as_first_name_with_middle_name",
            "raw": "della alex fennel",
            "first": "della",
            "middle": "alex",
            "last": "fennel",
        },
        {
            "id": "della_as_first_name_with_multiple_middle_name",
            "raw": "della alex eggers fennel",
            "first": "della",
            "middle": "alex eggers",
            "last": "fennel",
        },
        {
            "id": "della_as_prefix_excludes_middle",
            "raw": "alex della fennel",
            "first": "alex",
            "last": "della fennel",
        },
        {
            "id": "della_as_last_name",
            "raw": "alex eggers della",
            "first": "alex",
            "middle": "eggers",
            "last": "della",
        },
        {
            "id": "della_as_last_name2",
            "raw": "della, alex eggers",
            "first": "alex",
            "middle": "eggers",
            "last": "della",
        },
        {
            "id": "della_as_last_name",
            "raw": "alex eggers della jr",
            "first": "alex",
            "middle": "eggers",
            "last": "della",
            "suffix": "jr",
        },
        {
            "id": "della_as_first_middle_name",
            "raw": "alex della eggers fennel",
            "first": "alex",
            "middle": "della eggers",
            "last": "fennel",
        },
        {
            "id": "della_with_clear_split_to_middle",
            "raw": "fennel, alex della",
            "first": "alex",
            "middle": "della",
            "last": "fennel",
        },
        {
            "id": "de_la_too",
            "raw": "alex de la fennel",
            "first": "alex",
            "last": "de la fennel",
        },
        {
            "id": "von_der_too",
            "raw": "alex von der fennel",
            "first": "alex",
            "last": "von der fennel",
        },
        {
            "id": "de_la_too2",
            "raw": "de la fennel, alex",
            "first": "alex",
            "last": "de la fennel",
        },
        {
            "id": "von_der_too",
            "raw": "von der fennel, alex",
            "first": "alex",
            "last": "von der fennel",
        },
    ],
)
def issue_26_della_and_van_current_behavior(entry):
    dict_entry_test(Name, entry)


@pytest.mark.parametrize(
    "entry",
    [
        {
            "raw": "bah loney, junior oni r q x",
            "last": "bah loney",
            "first": "junior",
            "middle": "oni r q x",
        }
    ],
)
def test_last_names_non_prefixed_try_for_coverage(entry):
    dict_entry_test(Name, entry)
