import pytest

from nominally.parser import Name
from .conftest import dict_entry_test


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
    raw = " ".join(static)
    assert set(static) <= set(Name(raw).values())


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


@pytest.mark.parametrize(
    "entry",
    [
        pytest.param(
            {
                "id": "della_as_first_name",
                "raw": "della fennel",
                "first": "della",
                "last": "fennel",
            }
        ),
        pytest.param(
            {
                "id": "della_as_first_name_with_middle_name",
                "raw": "della alex fennel",
                "first": "della",
                "middle": "alex",
                "last": "fennel",
            }
        ),
        pytest.param(
            {
                "id": "della_as_first_name_with_multiple_middle_name",
                "raw": "della alex eggers fennel",
                "first": "della",
                "middle": "alex eggers",
                "last": "fennel",
            }
        ),
        pytest.param(
            {
                "id": "della_as_prefix_excludes_middle",
                "raw": "alex della fennel",
                "first": "alex",
                "last": "della fennel",
            }
        ),
        pytest.param(
            {
                "id": "della_as_last_name",
                "raw": "alex eggers della",
                "first": "alex",
                "middle": "eggers",
                "last": "della",
            }
        ),
        pytest.param(
            {
                "id": "della_as_last_name2",
                "raw": "della, alex eggers",
                "first": "alex",
                "middle": "eggers",
                "last": "della",
            }
        ),
        pytest.param(
            {
                "id": "della_as_last_name",
                "raw": "alex eggers della jr",
                "first": "alex",
                "middle": "eggers",
                "last": "della",
                "suffix": "jr",
            }
        ),
        pytest.param(
            {
                "id": "della_as_first_middle_name",
                "raw": "alex della eggers fennel",
                "first": "alex",
                "middle": "della eggers",
                "last": "fennel",
            }
        ),
        pytest.param(
            {
                "id": "della_recaptured",
                "raw": "fennel, alex della",
                "first": "alex",
                "last": "della fennel",
            }
        ),
        pytest.param(
            {
                "id": "de_la_too",
                "raw": "alex de la fennel",
                "first": "alex",
                "last": "de la fennel",
            }
        ),
        pytest.param(
            {
                "id": "von_der_too",
                "raw": "alex von der fennel",
                "first": "alex",
                "last": "von der fennel",
            }
        ),
        pytest.param(
            {
                "id": "de_la_too2",
                "raw": "de la fennel, alex",
                "first": "alex",
                "last": "de la fennel",
            }
        ),
        pytest.param(
            {
                "id": "von_der_too",
                "raw": "von der fennel, alex",
                "first": "alex",
                "last": "von der fennel",
            }
        ),
        pytest.param(
            {
                "raw": "Johann Gambolputty de von Ausfern",
                "first": "johann",
                "middle": "gambolputty",
                "last": "de von ausfern",
            }
        ),
        pytest.param(
            {
                "raw": "Ausfern, Johann Gambolputty de von",
                "first": "johann",
                "middle": "gambolputty",
                "last": "de von ausfern",
            }
        ),
        pytest.param(
            {
                "raw": "Ausfern, Johann Gambolputty de von, Jr.",
                "first": "johann",
                "middle": "gambolputty",
                "last": "de von ausfern",
                "suffix": "jr",
            }
        ),
        pytest.param(
            {
                "raw": "Ausfern, Johann Gambolputty, de von, Jr.",
                "first": "johann",
                "middle": "gambolputty",
                "last": "de von ausfern",
                "suffix": "jr",
            }
        ),
    ],
)
def issue_26_and_issue_37_prefixes(entry):
    dict_entry_test(Name, entry)
