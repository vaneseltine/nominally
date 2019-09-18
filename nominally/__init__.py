"""nominally: a maximum-strength name parser for record linkage"""

import sys
import typing as T

from nominally.api import parse_name, report
from nominally.parser import Name

__version__ = "1.0.0"


def cli_parse(raw_name: T.Optional[str] = None) -> int:
    if sys.argv:
        sys.argv.pop(0)
    if not raw_name and (not sys.argv or sys.argv[0] in ("--help", "-h", "help")):
        return usage()
    if sys.argv and sys.argv[0] in ("--version", "-V"):
        return version()
    exit_code = report(raw_name or " ".join(sys.argv), details=True)
    return exit_code


def usage() -> int:
    print("nominally CLI example:", "-" * 80, sep="\n")
    print('> nominally "Mr. Eric (The Inspector) Praline"')
    cli_parse("Mr. Eric (The Inspector) Praline")
    print("-" * 80)
    return 0


def version() -> int:
    print(
        f"nominally {__version__} running on "
        f"Python {sys.version.split(' ')[0]} ({sys.executable})"
    )
    return 0
