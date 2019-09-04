import logging
import re

from unidecode import unidecode_expect_ascii

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(fmt)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


def lc(value):
    """Lower case and remove any periods to normalize for comparison."""
    if not value:
        return ""
    return value.lower().strip(".")


def clean(s, deep=False):
    s = unidecode_expect_ascii(s).lower()
    s = re.sub(r"[-_/\\]+", "-", s)
    s = re.sub(r"[^ \-a-z'\"()]+", "", s)
    s = re.sub(r"\s+", " ", s)  # condense spaces
    s = s.strip("- ")
    return s
