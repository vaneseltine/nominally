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


def clean(
    s,
    lowercase=True,
    substitute_hyphen=r"[-_/\\]+",
    substitute_nothing=r"[^ \-A-Za-z'\"()]+",
):
    if not isinstance(s, str):
        return ""
    s = unidecode_expect_ascii(s)
    s = re.sub(substitute_hyphen, "-", s)
    s = re.sub(substitute_nothing, "", s)
    s = re.sub(r"\s+", " ", s)
    s = s.strip("-")
    s = s.strip(" ")
    return s.lower()
