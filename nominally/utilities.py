import typing as T


def flatten_once(nested_list: T.List[T.Any]) -> T.List[T.Any]:
    return [item for sublist in nested_list for item in sublist]


def remove_falsy(seq: T.List[T.Any]) -> T.List[T.Any]:
    if not isinstance(seq, list):
        return seq
    return [x for x in map(remove_falsy, seq) if x]


def prettier_print(dictionary: T.Mapping[str, T.Any]) -> None:
    """pprint.pprint unacceptably sorts"""
    for k, v in dictionary.items():
        print(f"{k:>10}: {v}")
