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

        pieces, working = self.pre_process(self.original)
        working = self.parse_full_name(pieces, working)
        self._final = self.post_process(working)
        logger.debug(f"Final: {repr(self._final)}")

        pieces, working = self.pre_process(self.original)
        logger.debug(f"1 {repr(pieces)}")
        logger.debug(f"1 {repr(working)}")
        pieces, working["suffix"] = self.extract_suffixes(pieces)
        logger.debug(f"2 {repr(pieces)}")
        logger.debug(f"2 {repr(working)}")
        pieces, working["title"] = self.extract_title(pieces)
        logger.debug(f"3 {repr(pieces)}")
        logger.debug(f"3 {repr(working)}")
        if len(pieces) == 1:
            logger.debug("#TODO: prefix, conj, and pull out last and first")
            logger.info(pieces)
        elif len(pieces) == 2:
            logger.debug("#TODO: pull out last, then prefix/conj first and mid")
            logger.info(pieces)
        else:
            logger.critical(pieces)
            raise RuntimeError(f"{repr(pieces)}: more parts than anticipated")
            exit()
        self._NEW_final = self.post_process(working)
        logger.debug(f"New final: {repr(self._NEW_final)}")
        if self.unparsable:
            logger.info('Unparsable: "%s" ', self.original)

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
        working = cls.make_single_name_last(working)
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

    @staticmethod
    def make_single_name_last(working: PiecesDict) -> PiecesDict:
        """
        If there are only two parts and one is a title, assume it's a last name
        instead of a first name. e.g. Mr. Johnson.
        """
        if working["title"] and len([x for x in working.values() if x]) == 2:
            working["first"], working["last"] = (working["last"], working["first"])
        return working

    @classmethod
    def new_working(cls) -> PiecesDict:
        return {k: [] for k in cls.keys()}

    @classmethod
    def parse_full_name(
        cls, pieces: Pieces, working: T.Optional[PiecesDict] = None
    ) -> PiecesDict:

        _working: PiecesDict = working or cls.new_working()

        # break up pieces into pieces by commas
        logger.debug(f"pieces    in  {repr(pieces)}")
        logger.debug(f"working   in  {repr(_working)}")

        if len(pieces) == 1:
            _working = cls.parse_v_no_commas(pieces, _working)

        else:
            # if all the end pieces are suffixes and there is more than one piece
            # in the first part. (Suffixes will never appear after last names
            # only, and allows potential first names to be in suffixes, e.g.
            # "Johnson, Bart"
            if is_only_suffixes(pieces[1].split()) and len(pieces[0].split()) > 1:
                _working = cls.parse_v_suffix_comma(pieces, _working)
            else:
                _working = cls.parse_v_lastname_comma(pieces, _working)

        #  suffixes are not all fully pieced out above
        if _working["suffix"]:
            rejoined = " ".join(_working["suffix"])
            _working["suffix"] = rejoined.replace(",", " ").split()

        logger.debug(f"_working   out {repr(_working)}")
        return _working

    @classmethod
    def parse_v_suffix_comma(cls, parts, working=None) -> PiecesDict:
        """
        suffix comma:
        title first middle last [suffix], suffix [suffix] [, suffix]
                       parts0,          parts1..
        """
        working = working or cls.new_working()

        working["suffix"] += parts[1:]
        pieces = cls.parse_pieces(parts[0].split())
        logger.debug(f"parts     in  {repr(parts)}")
        logger.debug(f"working   in  {repr(working)}")
        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None  # type: ignore

            if is_title(piece) and (nxt or len(pieces) == 1) and not working["first"]:
                working["title"].append(piece)
                continue
            if not working["first"]:
                working["first"].append(piece)
                continue
            if is_only_suffixes(pieces[i + 1 :]):
                working["last"].append(piece)
                working["suffix"] = pieces[i + 1 :] + working["suffix"]
                break
            if not nxt:
                working["last"].append(piece)
                continue
            working["middle"].append(piece)
        logger.debug(f"working   out {repr(working)}")
        return working

    @classmethod
    def parse_v_lastname_comma(cls, parts, working=None) -> PiecesDict:
        """
        lastname comma:
        last [suffix], title first middles[,] suffix [,suffix]
            parts0      parts1,              parts2..
        """
        working = working or cls.new_working()

        pieces = cls.parse_pieces(parts[1].split())

        logger.debug(f"parts     in  {repr(parts)}")
        logger.debug(f"working   in  {repr(working)}")

        # lastname part may have suffixes in it
        lastname_pieces = cls.parse_pieces(parts[0].split())
        for piece in lastname_pieces:
            # the first one is always a last name, even if it looks like
            # a suffix
            if is_suffix(piece) and working["last"]:
                working["suffix"].append(piece)
            else:
                working["last"].append(piece)

        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None  # type: ignore

            if is_title(piece) and (nxt or len(pieces) == 1) and not working["first"]:
                working["title"].append(piece)
                continue
            if not working["first"]:
                working["first"].append(piece)
                continue
            if is_suffix(piece):
                working["suffix"].append(piece)
                continue
            working["middle"].append(piece)
        if len(parts) > 2:
            working["suffix"] += parts[2:]
        logger.debug(f"working   out {repr(working)}")
        return working

    @classmethod
    def parse_v_no_commas(cls, parts, working=None) -> PiecesDict:
        """
        no commas, title first middle middle middle last suffix
                  part[0]
        """
        working = working or cls.new_working()

        pieces = cls.parse_pieces(parts)
        logger.debug(f"parts     in {repr(parts)}")
        logger.debug(f"working   in {repr(working)}")
        p_len = len(pieces)
        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None  # type: ignore

            # title must have a next piece, unless it's just a title
            if is_title(piece) and (nxt or p_len == 1) and not working["first"]:
                working["title"].append(piece)
                continue
            if not working["first"]:
                if p_len == 1 and working["nickname"]:
                    working["last"].append(piece)
                    continue
                working["first"].append(piece)
                continue
            if is_only_suffixes(pieces[i + 1 :]) or (
                # if the next piece is the last piece and a roman
                # numeral but this piece is not an initial
                is_roman_numeral(nxt)
                and i == p_len - 2
                and not is_an_initial(piece)
            ):
                working["last"].append(piece)
                working["suffix"] += pieces[i + 1 :]
                break
            if not nxt:
                working["last"].append(piece)
                continue

            working["middle"].append(piece)
        logger.debug(f"working   out {repr(working)}")
        return working

    @classmethod
    def parse_pieces(cls, parts) -> Pieces:
        """
        Split group of pieces down to individual words and
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

    @staticmethod
    def extract_title(pieces: Pieces) -> T.Tuple[Pieces, Pieces]:
        logger.debug(pieces)
        output: Pieces = []
        title: Pieces = []
        while pieces:
            next_cluster = pieces.pop(0).split()

            if next_cluster:
                first_word, *remainder = next_cluster
                if is_title(first_word):
                    de_prefixed_cluster = " ".join(remainder)
                    output = output + [de_prefixed_cluster] + pieces
                    return output, [first_word]

            output.append(" ".join(next_cluster))
        return output, title

    @staticmethod
    def extract_suffixes(pieces: Pieces) -> T.Tuple[Pieces, Pieces]:
        outgoing: Pieces = []
        suffixes: Pieces = []
        min_words = 2

        word_clusters = [piece.split() for piece in pieces]

        while word_clusters:

            rejoined_clusters = flatter(word_clusters)
            if count_words(rejoined_clusters + outgoing) <= min_words:
                rejoined_clusters.extend(outgoing)
                return rejoined_clusters, suffixes

            words = word_clusters.pop()

            min_words_remaining = 0 if is_only_suffixes(words) else 1
            while count_words(words) > min_words_remaining:

                rejoined_clusters = flatter(word_clusters) + words
                if count_words(rejoined_clusters + outgoing) <= min_words:
                    outgoing.extend(rejoined_clusters)
                    return outgoing, suffixes

                if not is_suffix(words[-1]):
                    break
                suffixes.append(words.pop())

            if words:
                outgoing.append(" ".join(words))

        outgoing.reverse()
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


def is_roman_numeral(value: str) -> bool:
    return bool(config.RE_ROMAN_NUMERAL.match(value))


def is_only_suffixes(thing: T.Union[str, T.Sequence[str]]) -> bool:
    if isinstance(thing, str):
        thing = thing.split()
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
