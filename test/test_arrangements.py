import pytest

from nominally.parser import Name

ARRANGEMENTS = [
    pytest.param("j. h. c. goatberger"),
    pytest.param("j. h. c. goatberger md"),
    pytest.param("j. h. c. goatberger ii."),
    pytest.param("j. h. c. goatberger junior"),
    pytest.param("j. h. c. goatberger ii. md"),
    pytest.param("j. h. c. goatberger junior md"),
    pytest.param("j. h. c. goatberger, ii."),
    pytest.param("j. h. c. goatberger, junior"),
    pytest.param("j. h. c. goatberger, ii. md"),
    pytest.param("j. h. c. goatberger, junior md"),
    pytest.param("j. h. c. goatberger, ii., md"),
    pytest.param("j. h. c. goatberger, junior, md"),
    pytest.param("goatberger, j. h. c., ii., md"),
    pytest.param("goatberger, j. h. c., junior, md"),
    pytest.param("goatberger, j. h. c., ii. md"),
    pytest.param("goatberger, j. h. c., junior md"),
    pytest.param("goatberger, j. h. c. ii. md"),
    pytest.param("goatberger, j. h. c. junior md"),
    pytest.param("goatberger, j. h. c., ii."),
    pytest.param("goatberger, j. h. c., junior"),
    pytest.param("goatberger, j. h. c. ii."),
    pytest.param("goatberger, j. h. c. junior"),
    pytest.param("goatberger, j. h. c. md"),
    pytest.param("junior h. c. goatberger"),
    pytest.param("junior h. c. goatberger md"),
    pytest.param("junior h. c. goatberger phd."),
    pytest.param("junior h. c. goatberger phd. md"),
    pytest.param("junior h. c. goatberger, phd."),
    pytest.param("junior h. c. goatberger, phd. md"),
    pytest.param("junior h. c. goatberger, phd., md"),
    pytest.param("goatberger, junior h. c., phd., md"),
    pytest.param("goatberger, junior h. c., phd. md"),
    pytest.param("goatberger, junior h. c. phd. md"),
    pytest.param("goatberger, junior h. c., phd."),
    pytest.param("goatberger, junior h. c. phd."),
    pytest.param("goatberger, junior h. c. md"),
    pytest.param("goatberger, junior h. c."),
    pytest.param("goatberger, phd., junior h. c.", marks=pytest.mark.xfail()),
    pytest.param("goatberger, ii., j. h. c.", marks=pytest.mark.xfail()),
    pytest.param("goatberger, junior, j. h. c.", marks=pytest.mark.xfail()),
]


# @pytest.mark.parametrize("incoming", ARRANGEMENTS)
# def test_suffix_extraction(incoming):
#     n_suffixes
#     assert False


@pytest.fixture(autouse=True)
def add_spacing():
    print("\n")
    yield
    print("\n")


@pytest.mark.parametrize("incoming", ARRANGEMENTS)
@pytest.mark.parametrize("pyramid", ["unit", "end-to-end"])
def test_arrangements(incoming, pyramid):

    firstname = "j" if "j." in incoming else "junior"

    if pyramid == "unit":
        empty = {k: [] for k in Name.keys()}
        remaining = incoming.replace(".", "")  # relevant part of pre_process()
        _, name_dict = Name.parse_full_name(remaining, working=empty)
    else:
        name_dict = {k: v.split() for k, v in dict(Name(incoming)).items()}
    print(pyramid, name_dict)

    assert (name_dict["first"], name_dict["middle"], name_dict["last"]) == (
        [firstname],
        ["h", "c"],
        ["goatberger"],
    )
    for sfx in ["ii", "md", "phd"]:
        assert (sfx in name_dict["suffix"]) == (sfx in incoming)

