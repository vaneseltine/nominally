import pytest

from nominally import Name


@pytest.mark.xfail
def issue_52_hyphenated_number():
    name = Name("¼,A,A")
    assert name.first == "a"
    assert name.last == "a"
