import pytest

from nominally.parser import remove_falsey


@pytest.mark.parametrize(
    "incoming, outgoing",
    [
        ([], []),
        ([[]], []),
        ([[], []], []),
        ([[""]], []),
        ([[""], []], []),
        ([["hi"], ["bob"]], [["hi"], ["bob"]]),
        ([["hi"], [], ["bob"]], [["hi"], ["bob"]]),
    ],
)
def test_remove_falsey(incoming, outgoing):
    assert remove_falsey(incoming) == outgoing
