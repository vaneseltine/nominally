import sys
import typing as T
from nominally.parser import Name


def parse_name(s: str, details: bool = False) -> T.Dict[str, T.Any]:
    name = Name(s)
    if details:
        return name.report()
    return dict(name)  # type: ignore


def cli_parse(raw_name: T.Optional[str] = None) -> int:
    if sys.argv:
        sys.argv.pop(0)
    raw_name = raw_name or " ".join(sys.argv)
    if not raw_name:
        print("Usage: nominally Mr. Eric Praline")
        return 64
    name = Name(raw_name)
    prettier_print(name.report())
    return 0


def prettier_print(dictionary: T.Mapping[str, T.Any]) -> None:
    """pprint.pprint unacceptably sorts"""
    for k, v in dictionary.items():
        print(f"{k:>10}: {v}")
