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
            "id": "della_as_prefix_excluding_middle",
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
    ],
)
def issue_26_della_and_van_current_behavior(entry):
    dict_entry_test(Name, entry)
