import logging
import re
import typing as T

from unidecode import unidecode_expect_ascii

from nominally import config

LOGS_ON = True

logger = logging.getLogger()
if LOGS_ON:
    logger.setLevel(logging.DEBUG)
    MESSAGE_FORMAT = "{levelname:<8s} {funcName:<16s} {lineno:<4} {message}"
    stream_handler = logging.StreamHandler()  # pylint:disable=invalid-name
    stream_handler.setFormatter(logging.Formatter(MESSAGE_FORMAT, style="{"))
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
else:
    logger.addHandler(logging.NullHandler())

Pieces = T.List[str]
PiecesDict = T.Dict[str, Pieces]


class Name:
    """A human name, broken down into individual components."""

    _keys = ("title", "first", "middle", "last", "suffix", "nickname")

    def __init__(self, raw: str = "") -> None:
        self.original = raw

        # pieces, working = self.pre_process(self.original)
        # working = self.parse_full_name(pieces, working)
        # self._OLD_final = self.post_process(working)
        # logger.debug(f"OLD final: {repr(self._OLD_final)}")

        logger.debug(f"0o {repr(self.original)}")
        logger.warning("pre_process")
        pieces, working = self.pre_process(self.original)
        logger.debug(f"1p {repr(pieces)}")
        logger.debug(f"1w {repr(working)}")
        logger.warning("extract_title")
        pieces, working["title"] = self.extract_title(pieces)
        logger.debug(f"2p {repr(pieces)}")
        logger.debug(f"2w {repr(working)}")
        logger.warning("extract_suffixes")
        pieces, working["suffix"] = self.extract_suffixes(pieces)
        logger.debug(f"3p {repr(pieces)}")
        logger.debug(f"3w {repr(working)}")

        working["first"], working["middle"], working["last"] = self.new_mainline(pieces)
        logger.debug(f"4 {repr(working)}")

        # working.update(first_middle_last)
        self._final = self.post_process(working)
        logger.debug(f"New final: {repr(self._final)}")
        if self.unparsable:
            logger.info('Unparsable: "%s" ', self.original)

    @classmethod
    def new_mainline(cls, pieces: Pieces) -> T.Generator[T.List[str], None, None]:
        # T.Tuple[Pieces, Pieces, Pieces]:
        building: PiecesDict = {"F": [], "M": [], "L": []}

        logger.warning(f"building {building}")

        guesses: PiecesDict = cls.guess_from_commas(pieces)

        logger.warning(f"guesses {guesses}")

        direct_guesses = {k: guesses.pop(k) for k in ("F", "M", "L") if k in guesses}

        logger.warning(f"direct_guesses {direct_guesses}")

        building.update(direct_guesses)

        logger.warning(f"building {building}")
        logger.warning(f"guesses {guesses}")

        if guesses:

            parse_key, final_pieces_to_parse = next(iter(guesses.items()))
            combined_bits = cls.parse_pieces(final_pieces_to_parse)
            if combined_bits and parse_key == "FML":
                guesses["L"] = [combined_bits.pop(-1)]
            if combined_bits:
                guesses["F"] = [combined_bits.pop(0)]
            guesses["M"] = combined_bits

            building.update(guesses)

            logger.warning(f"building {building}")

        final_output = (building.get(x, []) for x in ["F", "M", "L"])
        return final_output

    @classmethod
    def guess_from_commas(cls, pieces: Pieces) -> PiecesDict:
        if len(pieces) == 1:
            return {"FML": [pieces[0]]}
        if len(pieces) == 2:
            return {"FM": [pieces[1]], "L": [pieces[0]]}
        logger.warning(f"{repr(pieces)}: more parts than anticipated")
        return {"L": [pieces[0]], "F": [pieces[1]], "M": pieces[2:]}

    @classmethod
    def pre_process(
        cls, s: str, working: T.Optional[PiecesDict] = None
    ) -> T.Tuple[Pieces, PiecesDict]:
        if working is None:
            working = {k: [] for k in cls.keys()}
        s = s.lower()
        s, working = cls.parse_nicknames(s, working)
        s = clean_input(s)
        return cls.string_to_pieces(s), working

    @staticmethod
    def string_to_pieces(remaining: str) -> Pieces:
        return re.split(r"\s*,\s*", remaining)

    @classmethod
    def post_process(cls, working: PiecesDict) -> PiecesDict:
        return working

    @staticmethod
    def parse_nicknames(
        remaining: str, working: PiecesDict
    ) -> T.Tuple[str, PiecesDict]:
        """
        The content of parenthesis or quotes in the name will be added to the
        nicknames list. This happens before any other processing of the name.

        Single quotes cannot span white space characters and must border
        white space to allow for quotes in names like O'Connor and Kawai'ae'a.
        Double quotes and parenthesis can span white space.
        """

        for pattern in (
            config.RE_QUOTED_WORD,
            config.RE_DOUBLE_QUOTES,
            config.RE_PARENTHESIS,
        ):
            if pattern.search(remaining):
                working["nickname"] += [x for x in pattern.findall(remaining)]
                remaining = pattern.sub("", remaining)
        return remaining, working

    @classmethod
    def parse_pieces(cls, parts: Pieces) -> Pieces:
        """
        Split list of pieces down to individual words and
            - join on conjuctions if appropriate
            - add prefixes to last names if appropriate
        """
        words = cls.break_down_to_words(parts)
        pieces = cls.combine_conjunctions(words)
        pieces = cls.combine_prefixes(pieces)
        return pieces

    @staticmethod
    def break_down_to_words(parts: Pieces) -> Pieces:
        return [word for part in parts for word in part.split()]

    # item for row in matrix for item in row]
    @staticmethod
    def combine_conjunctions(words: Pieces) -> Pieces:
        if len(words) < 4:
            return words

        result: Pieces = []
        queued = words.copy()
        while queued:
            word = queued.pop(-1)
            if is_conjunction(word) and result and queued:
                clause = [queued.pop(-1), word, result.pop(0)]
                word = " ".join(clause)
            result.insert(0, word)
        return result

    @staticmethod
    def combine_prefixes(words: Pieces) -> Pieces:
        if len(words) < 3:
            return words

        result: Pieces = []
        queued = words.copy()
        while queued:
            word = queued.pop(-1)
            if is_prefix(word) and result:
                accumulating: Pieces = []
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
    def title(self) -> str:
        return " ".join(self._final["title"]) or ""

    @property
    def first(self) -> str:
        return " ".join(self._final["first"]) or ""

    @property
    def middle(self) -> str:
        return " ".join(self._final["middle"]) or ""

    @property
    def last(self) -> str:
        return " ".join(self._final["last"]) or ""

    @property
    def suffix(self) -> str:
        return " ".join(self._final["suffix"]) or ""

    @property
    def nickname(self) -> str:
        return " ".join(self._final["nickname"]) or ""

    @property
    def unparsable(self) -> bool:
        return len(self) == 0

    def __len__(self) -> int:
        return len([v for v in dict(self).values() if v])  # type: ignore

    def __eq__(self, other: T.Any) -> bool:
        if self.unparsable:
            return False
        return str(self) == str(other)

    def __getitem__(self, key: str) -> T.Any:
        if key not in self.keys():
            true_key = self.keys()[key]  # type: ignore
            return self[true_key]
        return getattr(self, key)

    def __str__(self) -> str:
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

    def __repr__(self) -> str:
        if self.unparsable:
            text = "Unparsable"
        else:
            text = str(dict(self))  # type: ignore
        return f"{self.__class__.__name__}({text})"

    @classmethod
    def keys(cls) -> T.Tuple[str, ...]:
        return cls._keys

    def values(self):
        # TODO integrate better as dict
        return tuple(self[k] for k in self.keys())

    @staticmethod
    def extract_title(pieces: Pieces) -> T.Tuple[Pieces, Pieces]:
        logger.debug(pieces)
        outgoing: Pieces = []
        while pieces:
            next_cluster = pieces.pop(0).split()

            if next_cluster:
                first_word, *remainder = next_cluster
                if is_title(first_word):
                    de_prefixed_cluster = " ".join(remainder)
                    outgoing = outgoing + [de_prefixed_cluster] + pieces
                    return outgoing, [first_word]

            outgoing.append(" ".join(next_cluster))
        return outgoing, []

    @staticmethod
    def extract_suffixes(pieces: Pieces) -> T.Tuple[Pieces, Pieces]:

        logger.debug("extract_suffixes")
        logger.debug(f"pieces   {repr(pieces)}")

        outgoing: Pieces = []
        suffixes: Pieces = []
        # logger.debug(f"outgoing {repr(outgoing)}")
        # logger.debug(f"suffixes {repr(suffixes)}")

        min_words = 2

        word_clusters = [piece.split() for piece in pieces]

        while word_clusters:

            rejoined_clusters = flatter(word_clusters)
            if count_words(rejoined_clusters + outgoing) <= min_words:
                rejoined_clusters.extend(outgoing)
                logger.debug("1")
                return rejoined_clusters, suffixes

            words = word_clusters.pop()

            min_words_remaining = 0 if is_only_suffixes(words) else 1
            while count_words(words) > min_words_remaining:
                rejoined_clusters = flatter(word_clusters) + words
                logger.debug(f"rejoined_clusters {rejoined_clusters}")
                logger.debug(f"outgoing {outgoing}")
                if count_words(rejoined_clusters + outgoing) <= min_words:
                    outgoing.extend(rejoined_clusters)
                    outgoing = [" ".join(outgoing)]
                    logger.debug(f"outgoing OUT {outgoing}")
                    logger.debug("2")
                    return outgoing, suffixes

                if not is_suffix(words[-1]):
                    break
                suffixes.insert(0, words.pop())

            if words:
                outgoing.append(" ".join(words))

        outgoing.reverse()
        logger.debug("3")
        return outgoing, suffixes


def pieces_to_words(pieces: T.Sequence[str]) -> T.Sequence[str]:
    return " ".join(pieces).split()


def count_words(pieces: T.Sequence[T.Any]) -> int:
    return len(pieces_to_words(pieces))


def is_title(value: str) -> bool:
    return value in config.TITLES


def is_conjunction(piece: str) -> bool:
    return piece.lower() in config.CONJUNCTIONS and not is_an_initial(piece)


def is_prefix(piece: str) -> bool:
    return piece in config.PREFIXES


def is_only_suffixes(thing: T.Sequence[str]) -> bool:
    return all(is_suffix(x) for x in thing)


def is_suffix(piece: str) -> bool:
    return piece in (config.SUFFIXES) and not is_an_initial(piece)


def is_an_initial(value: str) -> bool:
    return bool(config.RE_INITIAL.match(value))


def clean_input(s: str) -> str:
    # Note: nicknames have already been removed
    s = unidecode_expect_ascii(s).lower()
    s = re.sub(r'"|`', "'", s)  # convert all quotes/ticks to single quotes
    s = re.sub(r";|:|,", ", ", s)  # convert : ; , to , with spacing
    s = re.sub(r"[-_/\\:]+", "-", s)  # convert _ / \ - : to single hyphen
    s = re.sub(r"[^-\sa-z0-9',]+", "", s)  # drop most all but - ' ,
    s = re.sub(r"\s+", " ", s)  # condense all whitespace to single space
    s = s.strip("- ")  # drop leading/trailing hyphens and spaces
    return s


def flatter(clusters: T.List[Pieces]) -> Pieces:
    return [" ".join(x) for x in clusters]


def parse_name(s: str) -> PiecesDict:
    return dict(Name(s))  # type: ignore
