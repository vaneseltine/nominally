import pytest

from nominally import Name


@pytest.mark.parametrize(
    "incoming",
    [
        ([[""]]),
        ([[""], []]),
        ([[], [""]]),
        ([[""], [""]]),
        ([[""], [""]]),
        ([[""], [""]]),
        ([[""], [""]]),
        ([[""], [""]]),
    ],
)
def test_parse_fml_with_blanks(incoming):
    assert Name._lfm_from_list(incoming) == {"first": [], "middle": [], "last": []}


@pytest.mark.parametrize(
    "incoming, f, m, l",
    [
        # ([[]], [], [], []),
        # ([], [], [], []),
        ([["last"], ["first"], ["middle"]], ["first"], ["middle"], ["last"]),
        ([["last"], ["first"]], ["first"], [], ["last"]),
        ([["first", "middle", "last"]], ["first"], ["middle"], ["last"]),
        ([["first", "last"]], ["first"], [], ["last"]),
        ([["last"], ["first", "middle"]], ["first"], ["middle"], ["last"]),
        ([["last"], ["first", "m1", "m2"]], ["first"], ["m1", "m2"], ["last"]),
        ([["last"], ["f1", "f2"], ["middle"]], ["f1", "f2"], ["middle"], ["last"]),
        ([["last"], ["first"], ["m1"], ["m2"]], ["first"], ["m1", "m2"], ["last"]),
        (
            [["last"], ["first"], ["m1"], ["m2"], ["m3"]],
            ["first"],
            ["m1", "m2", "m3"],
            ["last"],
        ),
        ([["last"], ["first", "m1 m2"]], ["first"], ["m1 m2"], ["last"]),
    ],
)
def test_parse_fml(incoming, f, m, l):
    answer = {"first": f, "middle": m, "last": l}
    assert Name._lfm_from_list(incoming) == answer
