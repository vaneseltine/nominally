"""
hypothesis-driven input testing.
Note that attempts to print the hypothesis output may fail due to console encoding;
a failure to print is not necessarily a failure to parse.
"""
import hypothesis as h
import hypothesis.strategies as s
import pytest

from nominally.parser import Name

MAX_EXAMPLES = 1000
DEADLINE = None

# Surrogate character \udd9b will be ignored. You might be using a narrow Python build.
UNIDECODE_SURROGATE_WARNING = "ignore:Surrogate character '"


@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@h.given(raw=s.text())
@h.settings(max_examples=MAX_EXAMPLES, deadline=DEADLINE)
def test_alphabetical_text_does_not_break(raw):
    _ = Name(raw).raw


@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@h.given(raw=s.characters())
@h.settings(max_examples=MAX_EXAMPLES, deadline=DEADLINE)
def test_characters_do_not_break(raw):
    _ = Name(raw).raw


@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@h.given(raw1=s.characters(), raw2=s.characters(), raw3=s.characters())
@h.settings(max_examples=MAX_EXAMPLES, deadline=DEADLINE)
def test_commas_do_not_break(raw1, raw2, raw3):
    _ = Name(f"{raw1},{raw2}").raw
    _ = Name(f"{raw1},{raw2},{raw3}").raw


# Failing on https://github.com/vaneseltine/nominally/issues/52
@pytest.mark.xfail
@pytest.mark.filterwarnings(UNIDECODE_SURROGATE_WARNING)
@h.given(raw1=s.characters(), raw2=s.characters(), raw3=s.characters())
@h.settings(max_examples=MAX_EXAMPLES, deadline=DEADLINE)
def test_idempotence_madness_for_breakage(raw1, raw2, raw3):
    name = Name(f"{raw1},{raw2},{raw3}")
    assert str(name) == str(Name(str(name)))


# Failing on https://github.com/vaneseltine/nominally/issues/52
@pytest.mark.xfail
@pytest.mark.parametrize(
    "raw", ["0,/,A", "0,',\"", "sr, a", "a, sr", "',A,A", '",A,A', "㈠,㈪,0"]
)
def test_failures_found_by_hypothesis(raw):
    name = Name(raw)
    assert str(name) == str(Name(str(name)))


def issue_42_keeping_quote_in_cleaned():
    name = Name('",A,A"')
    assert str(name) == str(Name(str(name)))


def issue_40_smart_quotes():
    name = Name("Bergholt “BSJ” Johnson")
    assert name.nickname
