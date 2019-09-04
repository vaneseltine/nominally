import pytest

from nominally.util import clean


class TestClean:
    @pytest.mark.parametrize(
        "raw", ["DINSDALE", "Dinsdale", "dINSDALE", "dinsdale", "DiNsDaLe"]
    )
    def t_force_lower(self, raw):
        assert clean(raw) == "dinsdale"

    @pytest.mark.parametrize(
        "raw", ["DINSDALE", "Dinsdale", "dINSDALE", "dinsdale", "DiNsDaLe"]
    )
    def t_force_lower(self, raw):
        assert clean(raw) == "dinsdale"

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
        assert clean(raw) == "spiny norman"

    @pytest.mark.parametrize("raw", ["Mr Εric Πραλiñé"])
    def t_convert_unicode(self, raw):
        """This is handled by unidecode and should not be extensively tested"""
        assert clean(raw) == "mr eric praline"

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
        assert clean(raw) == "mr eric praline"

    @pytest.mark.parametrize(
        "raw",
        [
            r"!M!r Eri!c Praline!!",
            r"//Mr Eric Praline",
            r"M2r Er4ic Pra32lin5e",
            r"Mr Eric Praline_____",
            r"Mr Eric Praline",
            r"/Mr Eric Praline",
            r"Mr% Eric Pr#ali&ne",
        ],
    )
    def t_ignore_most_symbols(self, raw):
        assert clean(raw) == "mr eric praline"

    @pytest.mark.parametrize(
        "raw, cooked",
        [
            ("Dinsdale", "dinsdale"),
            ("(Dinsdale)", "(dinsdale)"),
            ("Dins-dale-", "dins-dale"),
            ("Dins/dale-", "dins-dale"),
            ("Dins_dale-", "dins-dale"),
            ("Dins'dale", "dins'dale"),
            ("'Dinsdale'", "'dinsdale'"),
            ('"Dinsdale"', '"dinsdale"'),
        ],
    )
    def t_keep_certain_symbols(self, raw, cooked):
        assert clean(raw) == cooked

    @pytest.mark.parametrize(
        "raw, cooked",
        [
            ("Dinsdale-", "dinsdale"),
            ("--Dinsdale--", "dinsdale"),
            ("---Dinsdale-", "dinsdale"),
        ],
    )
    def t_strip_margin_hyphens(self, raw, cooked):
        assert clean(raw) == cooked
