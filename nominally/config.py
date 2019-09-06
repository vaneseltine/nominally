import re

RE_INITIAL = re.compile(r"^(\w\.|[A-Z])?$")
RE_QUOTED_WORD = re.compile(r"(?<!\w)\'([^\s]*?)\'(?!\w)")
RE_DOUBLE_QUOTES = re.compile(r'"(.*?)"')
RE_PARENTHESIS = re.compile(r"\((.*?)\)")

# Pieces that should join to their neighboring pieces, e.g. "and", "y" and "&".
# "of" and "the" are also include to facilitate joining multiple titles,
# e.g. "President of the United States".
# Previously included: "&", "and", "et", "e", "of", "the", "und"
CONJUNCTIONS = {"y"}

# Cannot include things that could also be first names
TITLES = {"dr", "mr", "mrs", "ms"}

SUFFIX_OR_NAME = {"junior", "v", "vi", "ix", "x"}

# Cannot include things that could also be middle or last names
SUFFIX_NOT_NAME = {
    "jd",
    "md",
    "phd",
    "sr",
    "jr",
    "2",
    "2nd",
    "ii",
    "3",
    "3rd",
    "iii",
    "4",
    "4th",
    "iv",
    "5",
    "5th",
    # "v",
    "6",
    "6th",
    # "vi",
    "7",
    "7th",
    "vii",
    "8",
    "8th",
    "viii",
    "9",
    "9th",
    # "ix",
    "10",
    "10th",
    # "x",
}

SUFFIXES = SUFFIX_OR_NAME ^ SUFFIX_NOT_NAME

# Name pieces that appear before a last name. Prefixes join to the piece
# that follows them to make one new piece. They can be chained together, e.g
# "von der" and "de la". Because they only appear in middle or last names,
# they also signifiy that all following name pieces should be in the same name
# part, for example, "von" will be joined to all following pieces that are not
# prefixes or suffixes, allowing recognition of double last names when they
# appear after a prefixes. So in "pennie von bergen wessels MD", "von" will
# join with all following name pieces until the suffix "MD", resulting in the
# correct parsing of the last name "von bergen wessels".
PREFIXES = {
    "abu",
    "bin",
    "bon",
    "da",
    "dal",
    "de",
    "dei",
    "del",
    "dela",
    # "della",
    "delle",
    "delli",
    "dello",
    "der",
    "di",
    "do",
    "dos",
    "du",
    "ibn",
    "la",
    "le",
    "san",
    "santa",
    "st",
    "ste",
    "van",
    "vel",
    "von",
}
