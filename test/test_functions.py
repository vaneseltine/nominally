import pytest

from nominally.parser import Name


@pytest.mark.parametrize(
    "incoming, outgoing",
    (
        (["oni", "de", "la", "soul"], ["oni", "de la soul"]),
        (["oni", "von", "der", "kind"], ["oni", "von der kind"]),
        (["oni", "della", "soul"], ["oni", "della soul"]),
        (["oni", "bin", "baloney"], ["oni", "bin baloney"]),
        (["oni", "van", "mooface"], ["oni", "van mooface"]),
    ),
)
def test_prefix_combining(incoming, outgoing):
    assert Name.join_prefixes(incoming) == outgoing


@pytest.mark.parametrize(
    "static",
    (
        (["van", "jones"]),
        (["della", "jones"]),
        (["bin", "jones"]),
        (["abu", "jones"]),
        (["van", "jones"]),
        (["van", "jones"]),
    ),
)
def test_prefix_avoid_combining(static):
    assert Name.join_prefixes(static) == static
