SUFFIX_NOT_ACRONYMS = set(
    ["dr", "esq", "esquire", "jr", "jnr", "junior", "sr", "snr", "2", "ii", "iii", "iv"]
)
"""

Post-nominal pieces that are not acronyms. The parser does not remove periods
when matching against these pieces.

"""
SUFFIX_ACRONYMS = set(
    [
        "ae",
        "afc",
        "afm",
        "arrc",
        "bart",
        "bem",
        "bt",
        "cb",
        "cbe",
        "cfp",
        "cgc",
        "cgm",
        "ch",
        "chfc",
        "cie",
        "clu",
        "cmg",
        "cpa",
        "cpm",
        "csi",
        "csm",
        "cvo",
        "dbe",
        "dcb",
        "dcm",
        "dcmg",
        "dcvo",
        "dds",
        "dfc",
        "dfm",
        "dmd",
        "do",
        "dpm",
        "dsc",
        "dsm",
        "dso",
        "dvm",
        "ed",
        "erd",
        "gbe",
        "gc",
        "gcb",
        "gcie",
        "gcmg",
        "gcsi",
        "gcvo",
        "gm",
        "idsm",
        "iom",
        "iso",
        "jd",
        "kbe",
        "kcb",
        "kcie",
        "kcmg",
        "kcsi",
        "kcvo",
        "kg",
        "kp",
        "kt",
        "lg",
        "lt",
        "lvo",
        "ma",
        "mba",
        "mbe",
        "mc",
        "md",
        "mm",
        "mp",
        "msc" "msm",
        "mvo",
        "obe",
        "obi",
        "om",
        "phd",
        "phr",
        "pmp",
        "qam",
        "qc",
        "qfsm",
        "qgm",
        "qpm",
        "rd",
        "rrc",
        "rvm",
        "sgm",
        "td",
        "ud",
        "vc",
        "vd",
        "vrd",
    ]
)
"""

Post-nominal acronyms. Titles, degrees and other things people stick after their name
that may or may not have periods between the letters. The parser removes periods
when matching against these pieces.

"""
