import pytest

from nominally import Name


@pytest.mark.xfail()
def issue_38_leveraging_first_middle_comma_breaks_idempotence():
    raw = "von floogle, moogle mary, mcdoogle"
    name = Name(raw)
    namename = Name(str(name))
    assert dict(name) == dict(namename)
