import pytest

from nominally.parser import Name


@pytest.mark.parametrize(
    "incoming, outgoing",
    (
        (["oni", "de", "la", "soul"], ["oni", "de la soul"]),
        (["oni", "bin", "baloney"], ["oni", "bin baloney"]),
        (["oni", "van", "mooface"], ["oni", "van mooface"]),
    ),
)
def test_prefix_combining(incoming, outgoing):
    assert Name._combine_prefixes(incoming) == outgoing


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
    assert Name._combine_prefixes(static) == static


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
