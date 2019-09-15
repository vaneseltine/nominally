import pytest

from nominally.parser import Name


def only_weird_prefixes():
    assert Name("van de von der von")


@pytest.mark.parametrize(
    "incoming, outgoing",
    (
        (["oni", "de", "la", "soul"], ["oni", "de la soul"]),
        (["oni", "bin", "baloney"], ["oni", "bin baloney"]),
        (["oni", "van", "mooface"], ["oni", "van mooface"]),
    ),
)
def test_prefix_combining(incoming, outgoing):
    assert Name._combine_rightmost_prefixes(incoming) == outgoing


@pytest.mark.parametrize(
    "static",
    (
        (["van", "jones"]),
        (["della", "jones"]),
        (["bin", "jones"]),
        (["abu", "jones"]),
        (["von", "jones"]),
    ),
)
def test_prefix_avoid(static):
    assert Name._combine_rightmost_prefixes(static) == static


@pytest.mark.parametrize(
    "incoming, outgoing",
    (
        (["joe", "suerte", "y", "claro"], ["joe", "suerte y claro"]),
        (["joe", "suerte", "y", "claro"], ["joe", "suerte y claro"]),
    ),
)
def test_conjunction_combine(incoming, outgoing):
    assert Name._combine_conjunctions(incoming) == outgoing


@pytest.mark.parametrize(
    "static",
    (
        ["joe", "y", "blow"],
        ["joe", "blow", "y"],
        ["joe", "st.", "blow", "y"],
        ["y", "joe", "blow", "y"],
        ["y", "joe", "blow", "jr"],
    ),
)
def test_conjunction_avoid(static):
    assert Name._combine_conjunctions(static) == static


@pytest.mark.parametrize(
    "first, second",
    (
        ("Ewan Gordon Mc Gregor", "Mc Gregor, Ewan Gordon"),
        ("Ewan Gordon Mac Gregor", "Mac Gregor, Ewan Gordon"),
    ),
)
def issue_14_mc_and_mac_as_prefix(first, second):
    assert Name(first) == Name(second)


def issue_22_consistently_handle_of_prefixes_in_first_name():
    name1 = Name("de ook, van ook yolo moomoo")
    name2 = Name("van ook yolo moomoo de ook")
    assert name1 == name2
