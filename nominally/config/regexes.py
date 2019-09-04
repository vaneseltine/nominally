import re

REGEXES = {
    ("spaces", re.compile(r"\s+", re.U)),
    ("word", re.compile(r"(\w|\.)+", re.U)),
    ("mac", re.compile(r"^(ma?c)(\w{2,})", re.I | re.U)),
    ("initial", re.compile(r"^(\w\.|[A-Z])?$", re.U)),
    ("quoted_word", re.compile(r"(?<!\w)\'([^\s]*?)\'(?!\w)", re.U)),
    ("double_quotes", re.compile(r"\"(.*?)\"", re.U)),
    ("parenthesis", re.compile(r"\((.*?)\)", re.U)),
    ("roman_numeral", re.compile(r"^(x|ix|iv|v?i{0,3})$", re.I | re.U)),
    ("no_vowels", re.compile(r"^[^aeyiuo]+$", re.I | re.U)),
    ("period_not_at_end", re.compile(r".*\..+$", re.I | re.U)),
}
