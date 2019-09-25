from string import ascii_lowercase

import pytest

from nominally.api import (
    __version__,
    cli,
    cli_help,
    cli_report,
    cli_version,
    parse_name,
)
from nominally.parser import Name

SAMPLE_RAW = "Johnson, Jr., Dr. Bergholt (Bloody Stupid) stuttley"


def very_rough_clean(s):
    return "".join(c for c in s.lower() if c in (*ascii_lowercase, " "))


class TestParseName:
    def test_literally_just_dict_of_name(self):
        name = parse_name(SAMPLE_RAW)
        assert name == dict(Name(SAMPLE_RAW))

    def test_is_quiet(self, capsys):
        parse_name(SAMPLE_RAW)
        captured = capsys.readouterr()
        assert not captured.out
        assert not captured.err


class TestCLIFairlySimply:
    @pytest.mark.parametrize(
        "arg_in, string_out",
        [
            ("--help", "example"),
            ("-h", "example"),
            ("help", "example"),
            ("--version", __version__),
            ("-V", __version__),
            ("Bob", "bob"),
        ],
    )
    def test_cli_choices(self, capsys, arg_in, string_out):
        mock_argv = [None, arg_in]
        cli(mock_argv)
        captured = capsys.readouterr()
        assert string_out in captured.out
        assert not captured.err

    def test_raw_cli_run_does_not_break(self, capsys):
        cli()
        captured = capsys.readouterr()
        assert not captured.err

    def test_cli_report(self, capsys):
        cli_report(SAMPLE_RAW)
        substrings = (
            very_rough_clean(SAMPLE_RAW).split()
            + Name._keys
            + ["raw", "cleaned", "parsed"]
        )

        captured = capsys.readouterr()
        for subs in substrings:
            assert subs in captured.out
        assert not captured.err

    def test_cli_version(self, capsys):
        cli_version()
        captured = capsys.readouterr()
        assert __version__ in captured.out
        assert not captured.err

    def test_cli_help(self, capsys):
        cli_help()
        captured = capsys.readouterr()
        for s in ["nominally", "example"]:
            assert s in captured.out
        assert not captured.err
