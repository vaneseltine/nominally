import pytest

from nominally.parser import Name, logger

from .conftest import (
    load_bank,
    make_ids,
    verify_approximate_ordering_of_leftovers,
    pieces_to_words,
)


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_meta_no_pre_process_side_effects_these_names(entry):
    _, working = Name.pre_process(entry["raw"])
    assert not any(bool(v) for v in working.values())


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_ordering_end_to_end(entry):
    name_dict = dict(Name(entry["raw"]))
    assert name_dict == {key: entry.get(key, "") for key in name_dict.keys()}


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_suffix_extraction_has_correct_suffixes(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    _, suffixes = Name.extract_suffixes(scrubbed)
    assert set(suffixes) == set(entry.get("suffix", "").split())


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_suffix_extraction_did_not_mistrack_words(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    pieces, suffixes = Name.extract_suffixes(scrubbed)
    assert set(pieces_to_words(scrubbed)) == set(pieces_to_words(pieces + suffixes))


@pytest.mark.parametrize("entry", load_bank("ordering"), ids=make_ids)
def test_suffix_extraction_maintained_first_last_order(entry):
    scrubbed, _ = Name.pre_process(entry["raw"])
    pre_pieces = scrubbed.copy()
    post_pieces, _ = Name.extract_suffixes(scrubbed)
    verify_approximate_ordering_of_leftovers(pre_pieces, post_pieces)

