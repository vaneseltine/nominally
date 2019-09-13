import re

NO_WORD_BEHIND = r"(?<!\w)"
NO_WORD_AHEAD = r"(?!\w)"

NICKNAME_BOUNDARIES = (
    [NO_WORD_BEHIND + r"\'", r"\'" + NO_WORD_AHEAD],
    [r'"'] * 2,
    [r"\(", r"\)"],
)

NICKNAME_PATTERNS = [
    re.compile(open_pattern + r"(.*?)" + close_pattern)
    for open_pattern, close_pattern in NICKNAME_BOUNDARIES
]

SUFFIX_PATTERNS = {
    re.compile(NO_WORD_BEHIND + s + NO_WORD_AHEAD): generational
    for s, generational in [
        (r"\s*ph\.?d\.?", False),
        (r"\s*m\.?d\.?", False),
        (r"\s*jr\.?", True),
        (r"\s*ii?[iv]+?\.?", True),
    ]
}


# Pieces that should join to their neighboring pieces, e.g. "and", "y" and "&".
# "of" and "the" are also include to facilitate joining multiple titles,
# e.g. "President of the United States".
# Previously included: "&", "and", "et", "e", "of", "the", "und"
CONJUNCTIONS = {"y"}

# Cannot include things that could also be first names
TITLES = {"dr", "mr", "mrs", "ms"}

# Cannot include things that could also be middle or last names
POSSIBLE_NAME = {"junior"}
PROFESSIONAL_SUFFIX = {"jd", "md", "phd"}
GENERATIONAL_SUFFIX = {
    "sr",
    "junior",
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
}

SUFFIXES = GENERATIONAL_SUFFIX ^ PROFESSIONAL_SUFFIX
SUFFIX_OR_NAME = SUFFIXES & POSSIBLE_NAME

# Name pieces that appear before a last name. Prefixes join to the piece
# that follows them to make one new piece. They can be chained together, e.g
# "von der" and "de la".
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
    "della",
    "delle",
    "delli",
    "dello",
    "dem",
    "der",
    "di",
    "do",
    "dos",
    "du",
    "ibn",
    "la",
    "le",
    "mc",
    "mac",
    "san",
    "santa",
    "st",
    "ste",
    "van",
    "vel",
    "von",
}
