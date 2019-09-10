import typing as T

from nominally.parser import Name


def parse_name(s: str, details: bool = False) -> T.Dict[str, T.Any]:
    name = Name(s)
    if details:
        return name.report()
    return dict(name)  # type: ignore


def report(raw_name: str) -> int:
    name = Name(raw_name)
    prettier_print(name.report())
    return 0


def prettier_print(dictionary: T.Mapping[str, T.Any]) -> None:
    """pprint.pprint unacceptably sorts"""
    for k, v in dictionary.items():
        print(f"{k:>10}: {v}")
