# -*- coding: utf-8 -*-
"""The :py:mod:`nominally.config` module manages the configuration of nominally."""
import re
import sys

from nominally.util import lc


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

FIRST_NAME_TITLES = {}
TITLES = {"dr", "mr", "mrs", "ms", "phd", "sr", "sra", "srta"}

# Post-nominal pieces that are not acronyms. The parser does not remove periods
# when matching against these pieces.
SUFFIX_NOT_ACRONYMS = {"dr", "jr", "junior", "sr", "snr", "2", "ii", "iii", "iv"}

# Post-nominal acronyms. Titles, degrees and other things people stick after their name
# that may or may not have periods between the letters. The parser removes periods
# when matching against these pieces.
SUFFIX_ACRONYMS = {"jd", "ma", "mba", "mbe", "mc", "md", "msc", "msm", "phd"}

# Pieces that should join to their neighboring pieces, e.g. "and", "y" and "&".
# "of" and "the" are also include to facilitate joining multiple titles,
# e.g. "President of the United States".
CONJUNCTIONS = {"y"}  # "&", "and", "et", "e", "of", "the", "und", "y"}

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
    "degli",
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


class DotDict(dict):
    """A dictionary with dot.notation get access."""

    def __getattr__(self, attr):
        return self.get(attr)


class Constants(object):
    """
    An instance of this class hold all of the configuration constants for the parser.

    :param set prefixes:
        :py:attr:`prefixes` wrapped with :py:class:`SetManager`.
    :param set titles:
        :py:attr:`titles` wrapped with :py:class:`SetManager`.
    :param set first_name_titles:
        :py:attr:`~titles.FIRST_NAME_TITLES` wrapped with :py:class:`SetManager`.
    :param set suffix_acronyms:
        :py:attr:`~suffixes.SUFFIX_ACRONYMS`  wrapped with :py:class:`SetManager`.
    :param set suffix_not_acronyms:
        :py:attr:`~suffixes.SUFFIX_NOT_ACRONYMS`  wrapped with :py:class:`SetManager`.
    :param set conjunctions:
        :py:attr:`conjunctions`  wrapped with :py:class:`SetManager`.
    :type regexes: tuple or dict
    :param regexes:
        :py:attr:`regexes`  wrapped with :py:class:`DotDict`.
    """

    def __init__(
        self,
        prefixes=PREFIXES,
        suffix_acronyms=SUFFIX_ACRONYMS,
        suffix_not_acronyms=SUFFIX_NOT_ACRONYMS,
        titles=TITLES,
        conjunctions=CONJUNCTIONS,
        regexes=REGEXES,
    ):
        self.prefixes = prefixes
        self.suffix_acronyms = suffix_acronyms
        self.suffix_not_acronyms = suffix_not_acronyms
        self.titles = titles
        self.conjunctions = conjunctions
        self.regexes = DotDict(regexes)


#: A module-level instance of the :py:class:`Constants()` class.
#: Provides a common instance for the module to share
#: to easily adjust configuration for the entire module.
#: See `Customizing the Parser with Your Own Configuration <customize.html>`_.
CONSTANTS = Constants()
