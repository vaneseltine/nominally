import pytest

from nominally.parser import Name

ARRANGEMENTS = [
    "j. h. c. goatberger",
    "j. h. c. goatberger md",
    "j. h. c. goatberger jr.",
    "j. h. c. goatberger jr. md",
    "j. h. c. goatberger, jr.",
    "j. h. c. goatberger, jr. md",
    "j. h. c. goatberger, jr., md",
    "goatberger, j. h. c., jr., md",
    "goatberger, j. h. c., jr. md",
    "goatberger, j. h. c. jr. md",
    "goatberger, j. h. c., jr.",
    "goatberger, j. h. c. jr.",
    "goatberger, j. h. c. md",
]


@pytest.fixture(autouse=True)
def add_spacing():
    print("\n")
    yield
    print("\n")


@pytest.mark.parametrize("incoming", ARRANGEMENTS)
def test_arrangements_end_to_end(incoming):
    print("END_TO_END start", incoming)
    n = Name(incoming)
    assert (n["first"], n["middle"], n["last"]) == ("j", "h c", "goatberger")
    for sfx in ["jr", "md"]:
        assert (sfx in n["suffix"]) == (sfx in incoming)
    print("END_TO_END end", dict(n))


@pytest.mark.parametrize("incoming", ARRANGEMENTS)
def test_arrangements_unit(incoming):
    empty = {k: [] for k in Name.keys()}
    remaining = incoming.replace(".", "")  # relevant part of pre_process()
    remaining, working = Name.parse_full_name(remaining, working=empty)
    assert (working["first"], working["middle"], working["last"]) == (
        ["j"],
        ["h", "c"],
        ["goatberger"],
    )
    for sfx in ["jr", "md"]:
        assert (sfx in working["suffix"]) == (sfx in incoming)


# @pytest.mark.parametrize("incoming", ("goatberger, jr., j. h. c.",))
# @pytest.mark.xfail(reason="To be implemented")
# def test_failing_arrangements(incoming):
#     empty = {k: [] for k in Name.keys()}

#     n = Name(incoming)
#     assert (n.first, n.middle, n.last) == ("j", "h c", "goatberger")
#     for sfx in ["jr", "md"]:
#         assert (sfx in n.suffix) == (sfx in incoming)

