"""nominally: An opinionated name parser for record linkage."""

import sys
import typing as T
from nominally.parser import Name

__version__ = "0.9.1"


def parse_name(s: str, details: bool = False) -> T.Dict[str, T.Any]:
    name = Name(s)
    if details:
        return name.report()
    return dict(name)  # type: ignore


def cli_parse(raw_name: T.Optional[str] = None) -> int:
    if sys.argv:
        sys.argv.pop(0)
    if not sys.argv or sys.argv[0] in ("--help", "-h"):
        return usage()
    if sys.argv[0] in ("--version", "-V"):
        return version()
    raw_name = raw_name or " ".join(sys.argv)
    name = Name(raw_name)
    prettier_print(name.report())
    return 0


def usage() -> int:
    print("""Usage:\n  nominally "Mr. Eric (Inspector) Praline""")
    return 0


def version() -> int:
    print(
        f"nominally {__version__} running on "
        f"Python {sys.version.split(' ')[0]} ({sys.executable})"
    )
    return 0


def prettier_print(dictionary: T.Mapping[str, T.Any]) -> None:
    """pprint.pprint unacceptably sorts"""
    for k, v in dictionary.items():
        print(f"{k:>10}: {v}")
