import typing as T

from nominally.parser import Name


def parse_name(s: str) -> T.Dict[str, T.Any]:
    return dict(Name(s))


def report(raw_name: str, details: bool = True) -> int:
    name = Name(raw_name)
    output = name.report() if details else dict(name)
    prettier_print(output)
    return 0


def prettier_print(dictionary: T.Mapping[str, T.Any]) -> None:
    """pprint.pprint unacceptably sorts"""
    for k, v in dictionary.items():
        print(f"{k:>10}: {v}")
