import logging
import re

from unidecode import unidecode_expect_ascii

log = logging.getLogger("HumanName")
log.addHandler(logging.NullHandler())
log.setLevel(logging.ERROR)

text_type = str
binary_type = bytes


def u(x, encoding=None):
    return text_type(x)


text_types = (text_type, binary_type)


def lc(value):
    """Lower case and remove any periods to normalize for comparison."""
    if not value:
        return ""
    return value.lower().strip(".")


def clean(s):
    if not isinstance(s, str):
        return ""
    s = unidecode_expect_ascii(s).lower()
    s = re.sub(r"[-_/\\]+", "-", s)
    s = re.sub(r"(?<!\d)0{1,2}(?!\d)", "o", s)  # fix typo 0 -> O
    s = re.sub(r"[^ \-a-z'\"()]+", "", s)
    s = re.sub(r"\s+", " ", s)  # condense spaces
    s = s.strip("- ")
    return s
