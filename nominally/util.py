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
    replace_with_space=r"[\s/\\_]+",
    replace_with_none=r"[^ \-A-Za-z'\"()]+",
):
    if not isinstance(s, str):
        return ""
    s = unidecode_expect_ascii(s)
    s = re.sub(replace_with_space, " ", s)
    s = re.sub(replace_with_none, "", s)
    s = s.lower().strip()
    return s
