import pytest

from nominally.utilities import flatten_once, remove_falsy


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
def test_remove_falsy(incoming, outgoing):
    assert remove_falsy(incoming) == outgoing


class TestFlatten:
    @pytest.mark.parametrize(
        "incoming",
        (
            [],
            [[]],
            [[], []],
            [[], [], []],
            [[], [], []],
            [[], [], [], []],
            [[], [], [], [], []],
            [[], [], [], [], [], []],
        ),
    )
    def t_nothing_from_nothing_leaves_nothing(self, incoming):
        assert flatten_once(incoming) == []

    @pytest.mark.parametrize(
        "example",
        [
            {"in": [["spam"], ["eggs"]], "out": ["spam", "eggs"]},
            {"in": [["spam", "spam"], ["eggs"]], "out": ["spam", "spam", "eggs"]},
            {
                "in": [["spam", "spam"], ["eggs", "eggs"]],
                "out": ["spam", "spam", "eggs", "eggs"],
            },
        ],
    )
    def t_flatten_onces(self, example):
        assert flatten_once(example["in"]) == example["out"]

    def t_only_flatten_onces_one_level(self):
        assert flatten_once([["too", ["many"]], "nests"]) != ["too", "many", "nests"]

    # @pytest.mark.parametrize(
    #     "incoming, output",
    #     [
    #         (["spam"], ["spam"]),
    #         ([["spam"], ["eggs"]], ["spam", "eggs"]),
    #         ([["spam", ["eggs"]], "spam"], ["spam", "eggs", "spam"]),
    #         (
    #             ["spam", ["spam"], "spam", ["spam"], "spam", [["spam"]], [[]]],
    #             ["spam", "spam", "spam", "spam", "spam", "spam"],
    #         ),
    #     ],
    # )
    # def t_leaves_strings(self, incoming, output):
    #     assert list(flatten_once(incoming)) == output
