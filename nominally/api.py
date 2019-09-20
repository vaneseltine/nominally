import sys
import typing as T

from nominally.parser import Name
from nominally.utilities import prettier_print

__version__ = "1.0.3"


def parse_name(s: str) -> T.Dict[str, T.Any]:
    """ Return the core name attributes as a dict. """
    return dict(Name(s))


def report(raw_name: str, details: bool = True) -> int:
    """ Print name attributes to stdout. """
    name = Name(raw_name)
    output = name.report() if details else dict(name)
    prettier_print(output)
    return 0


def cli_parse(raw_name: T.Optional[str] = None) -> int:
    if raw_name:
        return report(raw_name, details=True)
    if not sys.argv[1:] or (set(sys.argv) & {"--help", "-h", "help"}):
        return usage()
    if set(sys.argv) & {"--version", "-V"}:
        return version()
    return report(" ".join(sys.argv[1:]), details=True)


def usage() -> int:
    print("nominally CLI example:", "-" * 80, sep="\n")
    example_name = "Mr. Arthur (Two Sheds) Jackson"
    print(f'> nominally "{example_name}"')
    cli_parse(example_name)
    print("-" * 80)
    return 0


def version() -> int:
    print(
        f"nominally {__version__} running on "
        f"Python {sys.version.split(' ')[0]} ({sys.executable})"
    )
    return 0
