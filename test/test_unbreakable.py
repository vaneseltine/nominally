import hypothesis.strategies as s
import pytest
from hypothesis import given, settings

from nominally.parser import Name

MAX_EXAMPLES = 2000

# Surrogate character \udd9b will be ignored. You might be using a narrow Python build.
UNIDECODE_SURROGATE_WARNING = "ignore:Surrogate character '"


@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@given(s=s.text())
@settings(max_examples=MAX_EXAMPLES)
def test_alphabetical_text_does_not_break(s):
    # Note that attempting to print the hypothesis output may not work
    _ = Name(s).raw


@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@given(s=s.characters())
@settings(max_examples=MAX_EXAMPLES)
def test_characters_do_not_break(s):
    # Note that attempting to print the hypothesis output may not work
    _ = Name(s).raw


@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@given(s1=s.characters(), s2=s.characters(), s3=s.characters())
@settings(max_examples=MAX_EXAMPLES)
def test_commas_do_not_break(s1, s2, s3):
    # Note that attempting to print the hypothesis output may not work
    _ = Name(f"{s1},{s2}").raw
    _ = Name(f"{s1},{s2},{s3}").raw
