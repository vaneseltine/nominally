"""nominally: A maximum-strength name parser for record linkage."""

import sys
import typing as T

from nominally.api import parse_name, report
from nominally.parser import Name

__version__ = "0.9.4"


def cli_parse(raw_name: T.Optional[str] = None) -> int:
    if sys.argv:
        sys.argv.pop(0)
    if not sys.argv or sys.argv[0] in ("--help", "-h"):
        return usage()
    if sys.argv[0] in ("--version", "-V"):
        return version()
    return report(raw_name or " ".join(sys.argv))


def usage() -> int:
    print("""Usage:\n  nominally "Mr. Eric (Inspector) Praline""")
    return 0


def version() -> int:
    print(
        f"nominally {__version__} running on "
        f"Python {sys.version.split(' ')[0]} ({sys.executable})"
    )
    return 0
