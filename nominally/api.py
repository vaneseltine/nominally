import sys
import typing as T

from nominally.parser import Name
from nominally.utilities import prettier_print

__version__ = "1.0.3"


def parse_name(s: str) -> T.Dict[str, T.Any]:
    """Parse into Name, return core name attributes as a dict.

    This is the simplest function interface to *nominally*.
    """
    return dict(Name(s))


def cli(raw_name: T.Optional[str] = None) -> int:
    """Simple CLI with a minimal set of options.

        1. Report of a single name (parse into details).
        2. Help via usage information. [help, -h, --help]
        3. Version information. [-V, --version]
    """
    if raw_name:
        return cli_report(raw_name, details=True)
    if not sys.argv[1:] or (set(sys.argv) & {"--help", "-h", "help"}):
        return cli_help()
    if set(sys.argv) & {"--version", "-V"}:
        return cli_version()
    return cli_report(" ".join(sys.argv[1:]), details=True)


def cli_report(raw_name: str, details: bool = True) -> int:
    """Parse into Name, output (core or report) attributes."""
    name = Name(raw_name)
    output = name.report() if details else dict(name)
    prettier_print(output)
    return 0


def cli_help() -> int:
    """Output help for command line usage"""
    horizontal_line = "-" * 80
    print("nominally CLI example:", horizontal_line, sep="\n")
    example_name = "Mr. Arthur (Two Sheds) Jackson"
    print(f'> nominally "{example_name}"')
    cli(example_name)
    print(horizontal_line)
    return 0


def cli_version() -> int:
    """Output version info and script location"""
    print(
        f"nominally {__version__} running on "
        f"Python {sys.version.split(' ')[0]} ({sys.executable})"
    )
    return 0
