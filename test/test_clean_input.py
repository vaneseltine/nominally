import pytest

from nominally.parser import Name


class TestCleanName:
    @pytest.mark.parametrize(
        "raw", ["DINSDALE", "Dinsdale", "dINSDALE", "dinsdale", "DiNsDaLe"]
    )
    def t_force_lower(self, raw):
        assert Name._clean_input(raw) == "dinsdale"

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
        assert Name._clean_input(raw) == "spiny norman"

    @pytest.mark.parametrize("raw", ["Mr Εric Πραλiñé"])
    def t_convert_unicode(self, raw):
        """This is handled by unidecode and should not be extensively tested"""
        assert Name._clean_input(raw) == "mr eric praline"

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
        assert Name._clean_input(raw) == "mr eric praline"

    @pytest.mark.parametrize(
        "raw",
        [
            "praline; mr eric",
            "praline: mr eric",
            "praline, mr eric",
            "praline;mr eric",
            "praline:mr eric",
            "praline,mr eric",
        ],
    )
    def t_colons_and_commas(self, raw):
        assert Name._clean_input(raw) == "praline, mr eric"

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
        assert Name._clean_input(raw) == "mr eric praline"

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
        assert Name._clean_input(raw) == cooked

    @pytest.mark.parametrize(
        "raw, cooked",
        [
            ("Dinsdale-", "dinsdale"),
            ("--Dinsdale--", "dinsdale"),
            ("---Dinsdale-", "dinsdale"),
        ],
    )
    def t_strip_margin_hyphens(self, raw, cooked):
        assert Name._clean_input(raw) == cooked
