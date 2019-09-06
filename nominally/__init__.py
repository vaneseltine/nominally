import sys
import typing as T
from nominally.parser import Name, parse_name


def parse(raw_name: T.Optional[str] = None) -> int:
    if sys.argv:
        sys.argv.pop(0)
    raw_name = raw_name or " ".join(sys.argv)
    if not raw_name:
        print("Usage: nominally Mr. Eric Praline")
        return 1
    name = Name(raw_name)
    output = {"raw": raw_name, "parsed": str(name)}
    output.update(dict(name))  # type: ignore
    prettier_print(output)
    print("list:", list(name))  # type: ignore
    # prettier_print(name._OLD_final)
    return 0


def prettier_print(dictionary: T.Mapping[str, T.Any]) -> None:
    """pprint.pprint unacceptably sorts"""
    for k, v in dictionary.items():
        print(f"{k:>10}: {v}")
