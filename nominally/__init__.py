import sys

from nominally.parser import Name


def parse():
    sys.argv.pop(0)
    raw_name = " ".join(sys.argv)
    if not raw_name:
        print("Usage: nominally Mr. Eric Praline")
        return 1
    name = Name(raw_name)
    output = {"raw": raw_name, "parsed": str(name)}
    output.update(name)
    prettier_print(output)
    print("list:", list(name))
    return 0


def prettier_print(dictionary):
    """pprint.pprint unacceptably sorts"""
    for k, v in dictionary.items():
        print(f"{k:>10}: {v}")
