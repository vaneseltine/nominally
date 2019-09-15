import typing as T

from nominally.parser import Name
from nominally.utilities import prettier_print


def parse_name(s: str) -> T.Dict[str, T.Any]:
    return dict(Name(s))


def report(raw_name: str, details: bool = True) -> int:
    name = Name(raw_name)
    output = name.report() if details else dict(name)
    prettier_print(output)
    return 0
