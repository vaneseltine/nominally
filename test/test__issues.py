import pytest

from nominally import Name
from nominally.config import PREFIXES

from .conftest import dict_entry_test


def issue_58_respect_basic_case():
    dict_entry_test(
        Name,
        {
            "raw": "Herve Corre",
            "first": "Herve",
            "last": "Corre",
        },
        skip_cleaning=True,
    )


def issue_58_allow_skipping_cleaning_to_preserve_accents():
    name = Name("Hervé Corre", skip_cleaning=True)
    assert name.first == "Hervé"
    assert name.last == "Corre"


@pytest.mark.parametrize(
    "raw, first, middle, last",
    [
        ("Antonia Ax:son Johnson", "Antonia", "Ax:son", "Johnson"),
        ("Elliot S! Maggin", "Elliot", "S!", "Maggin"),
    ],
)
def issue_58_allow_skipping_cleaning_to_preserve_punctuation(raw, first, middle, last):
    name = Name(raw, skip_cleaning=True)
    assert name.first == first
    assert name.middle == middle
    assert name.last == last


def issue_58_allow_skipping_cleaning_to_preserve_numbers():
    name = Name("2 Chainz", skip_cleaning=True)
    assert name.first == "2"
    assert name.last == "Chainz"


def issue_58_allow_skipping_cleaning_to_preserve_capitals():
    name = Name("Herve Le Corre", skip_cleaning=True)
    assert name.first == "Herve"
    assert name.middle == "Le"
    assert name.last == "Corre"


def issue_58_nofix_two_name_raw_despite_prefix():
    """
    This behavior is intended; an existing test uses "van nguyen" to capture the first
    name "van."
    """
    name = Name("de patris", prefixes={"de"})
    assert name.first == "de"
    assert name.last == "patris"


@pytest.mark.parametrize(
    "prefix_arg, first, middle, last",
    [
        (None, "herve", "pfx", "corre"),  # default argument goes to config.PREFIXES
        ({"pfx"} | PREFIXES, "herve", "", "pfx corre"),  # Now "pfx" is part of suffixes
        ({"pfx"}, "herve", "", "pfx corre"),  # Now "pfx" is the ONLY suffix
    ],
)
def issue_58_api_for_custom_prefixes(prefix_arg, first, middle, last):
    name = Name("herve pfx corre", prefixes=prefix_arg)
    assert name.first == first
    assert name.middle == middle
    assert name.last == last
