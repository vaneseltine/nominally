import pytest

from nominally import Name


@pytest.mark.parametrize(
    "entry",
    [
        pytest.param(
            {
                "raw": "von floogle, moogle mary, mcdoogle",
                "first": "moogle mary",
                "middle": "mcdoogle",
                "last": "von floogle",
            },
            marks=pytest.mark.xfail,
        )
    ],
)
def issue_38_leveraging_first_middle_comma_breaks_idempotence(entry):
    name = Name(entry["raw"])
    namename = Name(str(name))
    assert dict(name) == dict(namename)
