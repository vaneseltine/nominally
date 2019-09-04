import re

RE_SPACES = re.compile(r"\s+")
RE_INITIAL = re.compile(r"^(\w\.|[A-Z])?$")
RE_QUOTED_WORD = re.compile(r"(?<!\w)\'([^\s]*?)\'(?!\w)")
RE_DOUBLE_QUOTES = re.compile(r"\"(.*?)\"")
RE_PARENTHESIS = re.compile(r"\((.*?)\)")
RE_ROMAN_NUMERAL = re.compile(r"^(ii|iii|iv|vi|vii|viii|ix)$", re.I)

# Pieces that should join to their neighboring pieces, e.g. "and", "y" and "&".
# "of" and "the" are also include to facilitate joining multiple titles,
# e.g. "President of the United States".
CONJUNCTIONS = {"y"}  # "&", "and", "et", "e", "of", "the", "und", "y"}

# Cannot include things that could also be first names
TITLES = {"dr", "mr", "mrs", "ms"}

# Post-nominal pieces that are not acronyms. The parser does not remove periods
# when matching against these pieces.
SUFFIX_NOT_ACRONYMS = {"jr", "junior", "sr", "snr", "2", "ii", "iii", "iv"}

# Post-nominal acronyms. Titles, degrees and other things people stick after their name
# that may or may not have periods between the letters. The parser removes periods
# when matching against these pieces.
SUFFIX_ACRONYMS = {"jd", "ma", "mba", "mbe", "mc", "md", "msc", "msm", "phd"}

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
    "della",
    "delle",
    "delli",
    "dello",
    "der",
    "di",
    "dí",
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

