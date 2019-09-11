from hypothesis import given, settings
from hypothesis.strategies import text

from nominally.parser import Name


@given(s=text())
@settings(max_examples=100)
def test_we_do_not_break(s):
    assert Name("") != Name(s)


@given(s=text(min_size=32))
@settings(max_examples=100)
def test_we_still_do_not_break(s):
    print(Name(s))
    assert Name("") != Name(s)
