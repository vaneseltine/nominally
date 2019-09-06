from csv import DictReader, DictWriter
from pathlib import Path
from pprint import pprint
import sys

from nominally import parse_name

CSV_IN = Path(__file__).parent / "./names.csv"
CSV_OUT = CSV_IN.parent / f"{CSV_IN.stem}_parsed.csv"
NAME_FIELD = "fullname"

DATA = """fullname
Mr. Samuel "Sam" Vimes
Samuel "Young Sam" Vimes II.
Sybil Deirdre Olgivanna Ramkin-Vimes
Claude Maximillian Overton Transpire (CMOT) Dibbler
Gwinifer 'Old Mother' Blackcap
Jane Mary Betty Ann Pamela von Jones
John "Not-A-Vampire-At-All" Smith
"Dr Lawn, John (Mossy)"
"Vetinari, Havelock"
"""

CSV_IN.write_text(DATA)

with CSV_IN.open("r") as infile:
    reader = DictReader(infile)
    raw_names = [row[NAME_FIELD] for row in reader]

# parsed_basic = {raw_names}
parsed_basic = [{NAME_FIELD: raw, **parse_name(raw)} for raw in raw_names]

pprint(raw_names)
pprint(parsed_basic)

newline_arg = "" if sys.platform.startswith("win") else None
with CSV_OUT.open("w", newline=newline_arg) as outfile:
    writer = DictWriter(outfile, parsed_basic[0].keys())
    writer.writeheader()
    writer.writerows(parsed_basic)
