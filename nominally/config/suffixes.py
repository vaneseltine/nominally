"""
Post-nominal pieces that are not acronyms. The parser does not remove periods
when matching against these pieces.
"""
SUFFIX_NOT_ACRONYMS = {
    "dr",
    "esq",
    "esquire",
    "jr",
    "jnr",
    "junior",
    "sr",
    "snr",
    "2",
    "ii",
    "iii",
    "iv",
}

"""
Post-nominal acronyms. Titles, degrees and other things people stick after their name
that may or may not have periods between the letters. The parser removes periods
when matching against these pieces.
"""
SUFFIX_ACRONYMS = {"jd", "ma", "mba", "mbe", "mc", "md", "msc", "msm", "phd"}

