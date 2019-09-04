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
    print(str(name))
    print(name.as_dict())
    return 0
