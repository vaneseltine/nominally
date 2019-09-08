import logging
import re
import typing as T

from unidecode import unidecode_expect_ascii  # type: ignore

from nominally import config

logger = logging.getLogger("nominally")

Pieces = T.List[str]
PiecesList = T.List[Pieces]
PiecesDict = T.Dict[str, Pieces]


class Name:
    """A human name, broken down into individual components."""

    _keys = ("title", "first", "middle", "last", "suffix", "nickname")

    def __init__(self, raw: str = "") -> None:
        self.original = raw

        logger.debug(repr(raw))
        pieces, working = self.pre_process(self.original)
        logger.debug(pieces)
        logger.debug(working)
        pieces, working["title"] = self._extract_title(pieces)
        logger.debug(pieces)
        logger.debug(working)
        pieces, working["suffix"] = self._extract_suffixes(pieces)
        logger.debug(pieces)
        logger.debug(working)
        working["first"], working["middle"], working["last"] = self._parse_fml(pieces)
        logger.debug(working)
        self._final = working

        if self.unparsable:
            logger.info('Unparsable: "%s" ', self.original)

    def report(self) -> T.Dict[str, T.Any]:
        return {
            "raw": self.original,
            "parsed": str(self),
            "list": list(self),  # type: ignore
            **dict(self),  # type: ignore
        }

    @classmethod
    def _parse_fml(cls, pieces: Pieces) -> T.Tuple[Pieces, ...]:
        fml_keys = ("F", "M", "L")

        guesses: PiecesDict = cls.guess_from_commas(pieces)

        building: PiecesDict = {k: [] for k in fml_keys}
        direct_guesses = {k: guesses.pop(k) for k in fml_keys if k in guesses}
        building.update(direct_guesses)

        if guesses:
            parse_key, final_pieces_to_parse = next(iter(guesses.items()))
            combined_bits = cls.parse_pieces(final_pieces_to_parse)
            if combined_bits and parse_key == "FML":
                guesses["L"] = [combined_bits.pop(-1)]
            if combined_bits:
                guesses["F"] = [combined_bits.pop(0)]
            guesses["M"] = combined_bits
            building.update(guesses)

        final_output = tuple(building.get(x, []) for x in fml_keys)
        return final_output

    @classmethod
    def guess_from_commas(cls, pieces: Pieces) -> PiecesDict:
        if not pieces:
            return {}
        if len(pieces) == 1:
            return {"FML": [pieces[0]]}
        if len(pieces) == 2:
            return {"FM": [pieces[1]], "L": [pieces[0]]}
        logger.warning(f"{repr(pieces)}: more parts than anticipated")
        return {"F": [pieces[1]], "M": pieces[2:], "L": [pieces[0]]}

    @classmethod
    def pre_process(cls, s: str) -> T.Tuple[Pieces, PiecesDict]:
        logger.debug(repr(s))
        working: PiecesDict = {k: [] for k in cls.keys()}
        s = s.lower()
        s, working = cls._parse_nicknames(s, working)
        s = cls.clean_input(s)
        logger.debug(repr(s))
        pieces = cls.string_to_pieces(s) if s else []
        return pieces, working

    @staticmethod
    def clean_input(s: str) -> str:
        """Clean string; anticipating that nicknames have been removed"""
        s = unidecode_expect_ascii(s).lower()
        s = re.sub(r'"|`', "'", s)  # convert all quotes/ticks to single quotes
        s = re.sub(r";|:|,", ", ", s)  # convert : ; , to , with spacing
        s = re.sub(r"[-_/\\:]+", "-", s)  # convert _ / \ - : to single hyphen
        s = re.sub(r"[^-\sa-z0-9',]+", "", s)  # drop most all but - ' ,
        s = re.sub(r"\s+", " ", s)  # condense all whitespace to single space
        s = s.strip("- ")  # drop leading/trailing hyphens and spaces
        return s

    @staticmethod
    def string_to_pieces(remaining: str) -> Pieces:
        return [x for x in re.split(r"\s*,\s*", remaining) if x]

    @staticmethod
    def _parse_nicknames(s: str, working: PiecesDict) -> T.Tuple[str, PiecesDict]:
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
            if pattern.search(s):
                working["nickname"] += [x for x in pattern.findall(s)]
                s = pattern.sub("", s)
        return s, working

    @staticmethod
    def _extract_title(pieces: Pieces) -> T.Tuple[Pieces, Pieces]:
        outgoing: Pieces = []
        while pieces:
            next_cluster = pieces.pop(0).split()

            first_word, *remainder = next_cluster
            if is_title(first_word):
                de_prefixed_cluster = " ".join(remainder)
                outgoing = outgoing + [de_prefixed_cluster] + pieces
                return outgoing, [first_word]

            outgoing.append(" ".join(next_cluster))
        return outgoing, []

    @staticmethod
    # def _extract_suffixes(pieces: Pieces) -> T.Tuple[PiecesList, Pieces]:
    def _extract_suffixes(
        pieces: Pieces, min_names: int = 2
    ) -> T.Tuple[Pieces, Pieces]:

        incoming: PiecesList = [piece.split() for piece in pieces]

        out_pl: PiecesList = []
        out_suffixes: Pieces = []

        while incoming:
            handling = incoming.pop()
            while handling:
                banking: Pieces = []
                if (
                    sum(len(x) for x in (handling, banking))
                    + sum(count_words(pl) for pl in (incoming, out_pl))
                    <= min_names
                ):
                    banking = handling + banking
                    break
                word = handling.pop()
                if is_suffix(word):
                    out_suffixes.insert(0, word)
                else:
                    banking = handling + [word] + banking
                    break
            if banking:
                out_pl.insert(0, banking)

        return ([" ".join(x) for x in out_pl], out_suffixes)

    @classmethod
    def parse_pieces(cls, pieces: Pieces) -> Pieces:
        """
        Split list of pieces down to individual words and
            - join on conjuctions if appropriate
            - add prefixes to last names if appropriate
        """
        out_pieces = cls._break_down_to_words(pieces)
        out_pieces = cls._combine_conjunctions(out_pieces)
        out_pieces = cls._combine_prefixes(out_pieces)
        return out_pieces

    @staticmethod
    def _break_down_to_words(parts: Pieces) -> Pieces:
        return [word for part in parts for word in part.split()]

    @staticmethod
    def _combine_conjunctions(words: Pieces) -> Pieces:
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
    def _combine_prefixes(words: Pieces) -> Pieces:
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

    def values(self) -> T.Tuple[str, ...]:
        return tuple(self[k] for k in self.keys())


def count_words(piecelist: T.Sequence[T.Any]) -> int:
    return sum(len(x) for x in piecelist)


def is_title(value: str) -> bool:
    return value in config.TITLES


def is_conjunction(piece: str) -> bool:
    return piece.lower() in config.CONJUNCTIONS and not is_an_initial(piece)


def is_prefix(piece: str) -> bool:
    return piece in config.PREFIXES


def is_suffix(piece: str) -> bool:
    return piece in (config.SUFFIXES) and not is_an_initial(piece)


def is_an_initial(value: str) -> bool:
    return bool(config.RE_INITIAL.match(value))
