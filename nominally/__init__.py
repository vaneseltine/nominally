from nominally.parser import Name

import sys


def parse():
    sys.argv.pop(0)
    print(sys.argv)
    raw_name = " ".join(sys.argv)
    if not raw_name:
        print("Usage: nominally Mr. Eric Praline")
        return 1
    name = Name(raw_name)
    d = {"raw": raw_name, "parsed": str(name)}
    d.update(name.as_dict())
    prettier_print(d)
    return 0


def prettier_print(d):
    """pprint.pprint unacceptably sorts"""
    for k, v in d.items():
        print(f"{k:>10}: {v}")
