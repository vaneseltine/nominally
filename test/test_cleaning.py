import pytest

from nominally.parser import Name

from .conftest import dict_entry_test


class TestCleanName:
    @pytest.mark.parametrize(
        "raw", ["DINSDALE", "Dinsdale", "dINSDALE", "dinsdale", "DiNsDaLe"]
    )
    def t_force_lower(self, raw):
        assert Name.clean(raw) == "dinsdale"

    @pytest.mark.parametrize(
        "raw",
        [
            " ❤  Spiny Norman ",
            "Spiny Norman != 🐈 ",
            "Spiny Norman != 🐱 ",
            "Spiny Norman == 🐾 ",
        ],
    )
    def t_drop_emoji(self, raw):
        assert Name.clean(raw) == "spiny norman"

    @pytest.mark.parametrize("raw", ["Mr Εric Πραλiñé"])
    def t_convert_unicode(self, raw):
        """This is handled by unidecode and should not be extensively tested"""
        assert Name.clean(raw) == "mr eric praline"

    @pytest.mark.parametrize(
        "raw",
        [
            "Mr Eric Praline",
            "Mr Eric Praline ",
            " Mr Eric Praline",
            "Mr  Eric Praline",
            "Mr   Eric   Praline",
            "  Mr  Eric  Praline  ",
            "Mr Eric Praline \t",
            " \n Mr Eric Praline",
            "Mr Eric Praline \r",
            "Mr \r\n Eric Praline ",
        ],
    )
    def t_drop_spacing(self, raw):
        assert Name.clean(raw) == "mr eric praline"

    @pytest.mark.parametrize(
        "raw",
        [
            "praline; mr eric",
            "praline: mr eric",
            "praline : mr eric",
            "praline, mr eric",
            "praline , mr eric",
            "praline;mr eric",
            "praline:mr eric",
            "praline,mr eric",
        ],
    )
    def t_colons_and_commas(self, raw):
        assert Name.clean(raw) == "praline, mr eric"

    @pytest.mark.parametrize(
        "raw",
        [
            r"!M!r Eri!c Praline!!",
            r"//Mr Eric Praline",
            r"Mr Eric Praline_____",
            r"Mr Eric Praline",
            r"/Mr Eric Praline",
            r"Mr% Eric Pr#ali&ne",
        ],
    )
    def t_ignore_most_symbols(self, raw):
        assert Name.clean(raw) == "mr eric praline"

    @pytest.mark.parametrize(
        "raw, cooked",
        [
            ("Dinsdale", "dinsdale"),
            ("(Dinsdale)", "dinsdale"),
            ("Dins-dale-", "dins-dale"),
            ("Dins/dale-", "dins-dale"),
            ("Dins_dale-", "dins-dale"),
            ("Dins'dale", "dins'dale"),
            ("'Dinsdale'", "'dinsdale'"),
        ],
    )
    def t_handle_certain_symbols(self, raw, cooked):
        assert Name.clean(raw) == cooked

    @pytest.mark.parametrize(
        "raw, cooked",
        [
            ("Dinsdale-", "dinsdale"),
            ("--Dinsdale--", "dinsdale"),
            ("---Dinsdale-", "dinsdale"),
        ],
    )
    def t_strip_margin_hyphens(self, raw, cooked):
        assert Name.clean(raw) == cooked


def issue_4_clean_nicknames():
    name = Name("ang%ua (ba%%rky) uberwald")
    assert name.first == "angua"
    assert name.nickname == "barky"


@pytest.mark.parametrize(
    "entry",
    [
        {
            "raw": "alfred p. 2234-234-53294-1- howdidthatgetthere",
            "last": "howdidthatgetthere",
            "first": "alfred",
            "middle": "p",
        }
    ],
)
def issue_32_strip_hyphens(entry):
    dict_entry_test(Name, entry)
