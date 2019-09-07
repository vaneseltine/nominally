import pytest

from nominally.parser import Name

from .conftest import load_bank, make_ids, verify_approximate_ordering_of_leftovers


@pytest.mark.parametrize(
    "entry", load_bank("title") + load_bank("ordering"), ids=make_ids
)
def test_title_extracts(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    _, title = Name._extract_title(scrubbed)
    assert set(title) == set(entry.get("title", "").split())


@pytest.mark.parametrize(
    "entry", load_bank("title") + load_bank("ordering"), ids=make_ids
)
def test_title_ordering(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    pre_pieces = scrubbed.copy()
    post_pieces, _ = Name._extract_title(scrubbed)
    if "berg" in entry["raw"]:
        verify_approximate_ordering_of_leftovers(pre_pieces, post_pieces)


@pytest.mark.parametrize(
    "raw, post_suffix, post_title",
    [
        ("john hicks", "john hicks", "john hicks"),
        ("dr john hicks", "dr john hicks", "john hicks"),
        ("john hicks md", "john hicks", "john hicks"),
    ],
)
def test_no_split(raw, post_suffix, post_title):
    pieces, _ = Name._extract_suffixes([raw])
    assert pieces == [post_suffix]
    pieces, _ = Name._extract_title(pieces)
    assert pieces == [post_title]
