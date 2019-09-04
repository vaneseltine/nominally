import logging

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
