from string import ascii_lowercase

import pytest

from nominally.api import parse_name, report
from nominally.parser import Name

SAMPLE_RAW = "Johnson, Jr., Dr. Bergholt (Bloody Stupid) stuttley"


def very_rough_clean(s):
    return "".join(c for c in s.lower() if c in (*ascii_lowercase, " "))


def test_parse_name_is_just_name():
    name = parse_name(SAMPLE_RAW)
    assert name == Name(SAMPLE_RAW)


def test_parse_name_is_quiet(capsys):
    parse_name(SAMPLE_RAW)
    captured = capsys.readouterr()
    assert not captured.out
    assert not captured.err


@pytest.mark.parametrize(
    "substrings",
    very_rough_clean(SAMPLE_RAW).split() + Name._keys + ["raw", "cleaned", "parsed"],
)
def test_report_has_keys(capsys, substrings):
    report(SAMPLE_RAW)
    captured = capsys.readouterr()
    for subs in substrings:
        assert subs in captured.out
    assert not captured.err
