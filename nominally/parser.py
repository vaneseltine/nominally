import logging
import re

from unidecode import unidecode_expect_ascii

from nominally import config

LOGS_ON = True

logger = logging.getLogger()
if LOGS_ON:
    logger.setLevel(logging.DEBUG)
    MESSAGE_FORMAT = "{levelname:<8s} {funcName:<24s} {lineno:<4} {message}"
    stream_handler = logging.StreamHandler()  # pylint:disable=invalid-name
    stream_handler.setFormatter(logging.Formatter(MESSAGE_FORMAT, style="{"))
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
else:
    logger.addHandler(logging.NullHandler())


def parse_name(s):
    return dict(Name(s))


class Name:
    """A human name, broken down into individual components."""

    _keys = ("title", "first", "middle", "last", "suffix", "nickname")

    def __init__(self, raw=""):
        self.original = raw
        self._full_name = self.original.lower()
        self.__working = {k: [] for k in self.keys()}

        self.pre_process()
        self.parse_full_name()
        self.post_process()

    def __len__(self):
        return len([v for k, v in dict(self).items() if v])

    def __eq__(self, other):
        if self.unparsable:
            logger.warning("Unparsable!")
            return False
        return str(self) == str(other)

    def __getitem__(self, key):
        if key not in self.keys():
            true_key = self.keys()[key]
            return self[true_key]
        return getattr(self, key)

    def __str__(self):
        string_parts = [
            self.title,
            self.first,
            f'"{self.nickname}"' if self.nickname else "",
            self.middle,
            self.last,
            self.suffix,
        ]
        joined = " ".join(string_parts)
        return re.sub(r"\s+", " ", joined).strip()

    def __repr__(self):
        if self.unparsable:
            text = "Unparsable"
        else:
            text = str(dict(self))
        return f"{self.__class__.__name__}({text})"

    @classmethod
    def keys(cls):
        return cls._keys

    def pre_process(self):
        self.parse_nicknames()
        self.thoroughly_clean()

    def post_process(self):
        self.make_single_name_last()

    def parse_nicknames(self):
        """
        The content of parenthesis or quotes in the name will be added to the
        nicknames list. This happens before any other processing of the name.

        Single quotes cannot span white space characters and must border
        white space to allow for quotes in names like O'Connor and Kawai'ae'a.
        Double quotes and parenthesis can span white space.

        Loops through 3 :py:data:`~nominally.config.regexes.REGEXES`;
        `quoted_word`, `double_quotes` and `parenthesis`.
        """

        for pattern in (
            config.RE_QUOTED_WORD,
            config.RE_DOUBLE_QUOTES,
            config.RE_PARENTHESIS,
        ):
            if pattern.search(self._full_name):
                self.__working["nickname"] += [
                    x for x in pattern.findall(self._full_name)
                ]
                logger.debug(f"{pattern}, {self.__working['nickname']}")
                self._full_name = pattern.sub("", self._full_name)

    def thoroughly_clean(self):
        self._full_name = clean_input(self._full_name)

    def make_single_name_last(self):
        """
        If there are only two parts and one is a title, assume it's a last name
        instead of a first name. e.g. Mr. Johnson.
        """
        if self.title and len(self) == 2:
            self.__working["first"], self.__working["last"] = (
                self.__working["last"],
                self.__working["first"],
            )

    def parse_full_name(self):
        """The main parse method."""

        # break up full_name into pieces by commas
        pieces = re.split(r"\s*,\s*", self._full_name)

        logger.debug("full_name: %s", self._full_name)
        logger.debug("pieces: %s", pieces)

        if len(pieces) == 1:
            self.parse_v_no_commas(pieces)

        else:
            # if all the end pieces are suffixes and there is more than one piece
            # in the first part. (Suffixes will never appear after last names
            # only, and allows potential first names to be in suffixes, e.g.
            # "Johnson, Bart"
            if are_all_suffixes(pieces[1].split()) and len(pieces[0].split()) > 1:
                self.parse_v_suffix_comma(pieces)
            else:
                self.parse_v_lastname_comma(pieces)

        if self.unparsable:
            logger.info('Unparsable: "%s" ', self.original)

    def parse_v_suffix_comma(self, parts):
        # suffix comma:
        # * title first middle last [suffix], suffix [suffix] [, suffix]
        # *               parts0,          parts1..

        self.__working["suffix"] += parts[1:]
        pieces = self.parse_pieces(parts[0].split())
        logger.debug(f"parse_v_suffix_comma pieces: {pieces}")
        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None

            if is_title(piece) and (nxt or len(pieces) == 1) and not self.first:
                self.__working["title"].append(piece)
                continue
            if not self.first:
                self.__working["first"].append(piece)
                continue
            if are_all_suffixes(pieces[i + 1 :]):
                self.__working["last"].append(piece)
                self.__working["suffix"] = pieces[i + 1 :] + self.__working["suffix"]
                break
            if not nxt:
                self.__working["last"].append(piece)
                continue
            self.__working["middle"].append(piece)

    def parse_v_lastname_comma(self, parts):
        # lastname comma:
        # * last [suffix], title first middles[,] suffix [,suffix]
        # *     parts0      parts1,              parts2..
        pieces = self.parse_pieces(parts[1].split())

        logger.debug(f"parse_v_lastname_comma pieces: {pieces}")

        # lastname part may have suffixes in it
        lastname_pieces = self.parse_pieces(parts[0].split())
        for piece in lastname_pieces:
            # the first one is always a last name, even if it looks like
            # a suffix
            if is_suffix(piece) and self.__working["last"]:
                self.__working["suffix"].append(piece)
            else:
                self.__working["last"].append(piece)

        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None

            if is_title(piece) and (nxt or len(pieces) == 1) and not self.first:
                self.__working["title"].append(piece)
                continue
            if not self.first:
                self.__working["first"].append(piece)
                continue
            if is_suffix(piece):
                self.__working["suffix"].append(piece)
                continue
            self.__working["middle"].append(piece)
        if len(parts) > 2:
            self.__working["suffix"] += parts[2:]

    def parse_v_no_commas(self, parts):
        # ~ no commas, title first middle middle middle last suffix
        # ~           part[0
        pieces = self.parse_pieces(parts)
        logger.debug(f"parse_v_no_commas pieces: {pieces}")
        p_len = len(pieces)
        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None

            # title must have a next piece, unless it's just a title
            if is_title(piece) and (nxt or p_len == 1) and not self.first:
                self.__working["title"].append(piece)
                continue
            if not self.first:
                if p_len == 1 and self.nickname:
                    self.__working["last"].append(piece)
                    continue
                self.__working["first"].append(piece)
                continue
            if are_all_suffixes(pieces[i + 1 :]) or (
                # if the next piece is the last piece and a roman
                # numeral but this piece is not an initial
                is_roman_numeral(nxt)
                and i == p_len - 2
                and not is_an_initial(piece)
            ):
                self.__working["last"].append(piece)
                self.__working["suffix"] += pieces[i + 1 :]
                break
            if not nxt:
                self.__working["last"].append(piece)
                continue

            self.__working["middle"].append(piece)

    def parse_pieces(self, parts):
        """
        Split group of pieces down to individual words and
            - join on conjuctions if appropriate
            - add prefixes to last names if appropriate
        """
        words = self.break_down_to_words(parts)
        pieces = self.combine_conjunctions(words)
        pieces = self.combine_prefixes(pieces)
        return pieces

    @staticmethod
    def break_down_to_words(parts):
        words = []
        for part in parts:
            for word in part.split():
                words.append(word)
        return words

    @staticmethod
    def combine_conjunctions(words):
        if len(words) < 4:
            return words

        result = []
        queued = words.copy()
        while queued:
            word = queued.pop(-1)
            if is_conjunction(word) and result and queued:
                clause = [queued.pop(-1), word, result.pop(0)]
                word = " ".join(clause)
            result.insert(0, word)
        return result

    @staticmethod
    def combine_prefixes(words):
        if len(words) < 3:
            return words

        result = []
        queued = words.copy()
        while queued:
            word = queued.pop(-1)
            if is_prefix(word) and result:
                accumulating = []
                while result:
                    next_most_recent = result[0]
                    next_word = next_most_recent.split()[0]
                    if is_suffix(next_word):
                        break
                    if accumulating and is_prefix(next_word):
                        break
                    accumulating.append(result.pop(0))
                word = " ".join([word, *accumulating])
            result.insert(0, word)
        return result

    @property
    def title(self):
        return " ".join(self.__working["title"]) or ""

    @property
    def first(self):
        return " ".join(self.__working["first"]) or ""

    @property
    def middle(self):
        return " ".join(self.__working["middle"]) or ""

    @property
    def last(self):
        return " ".join(self.__working["last"]) or ""

    @property
    def suffix(self):
        return ", ".join(self.__working["suffix"]) or ""

    @property
    def nickname(self):
        return " ".join(self.__working["nickname"]) or ""

    @property
    def unparsable(self):
        return len(self) == 0


def is_title(value):
    return value in config.TITLES


def is_conjunction(piece):
    return piece.lower() in config.CONJUNCTIONS and not is_an_initial(piece)


def is_prefix(piece):
    return piece in config.PREFIXES


def is_roman_numeral(value):
    return bool(config.RE_ROMAN_NUMERAL.match(value))


def is_suffix(piece):
    return piece in config.SUFFIXES and not is_an_initial(piece)


def are_all_suffixes(pieces):
    return all(is_suffix(x) for x in pieces)


def is_an_initial(value):
    return bool(config.RE_INITIAL.match(value))


def clean_input(s):
    # Note: nicknames have already been removed
    s = unidecode_expect_ascii(s).lower()
    s = re.sub(r'"|`', "'", s)  # convert all quotes/ticks to single quotes
    s = re.sub(r";|:|,", ", ", s)  # convert : ; , to , with spacing
    s = re.sub(r"[-_/\\:]+", "-", s)  # convert _ / \ - : to single hyphen
    s = re.sub(r"[^-\sa-z0-9',]+", "", s)  # drop most all but - ' ,
    s = re.sub(r"\s+", " ", s)  # condense all whitespace to single space
    s = s.strip("- ")  # drop leading/trailing hyphens and spaces
    return s
