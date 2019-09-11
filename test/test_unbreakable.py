"""
hypothesis-driven input testing.
Note that attempts to print the hypothesis output may fail due to console encoding;
a failure to print is not necessarily a failure to parse.
"""
import hypothesis.strategies as s
import pytest
from hypothesis import given, settings

from nominally.parser import Name

MAX_EXAMPLES = 20

# Surrogate character \udd9b will be ignored. You might be using a narrow Python build.
UNIDECODE_SURROGATE_WARNING = "ignore:Surrogate character '"


@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@given(raw=s.text())
@settings(max_examples=MAX_EXAMPLES)
def test_alphabetical_text_does_not_break(raw):
    _ = Name(raw).raw


@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@given(raw=s.characters())
@settings(max_examples=MAX_EXAMPLES)
def test_characters_do_not_break(raw):
    _ = Name(raw).raw


@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@given(raw1=s.characters(), raw2=s.characters(), raw3=s.characters())
@settings(max_examples=MAX_EXAMPLES)
def test_commas_do_not_break(raw1, raw2, raw3):
    _ = Name(f"{raw1},{raw2}").raw
    _ = Name(f"{raw1},{raw2},{raw3}").raw
