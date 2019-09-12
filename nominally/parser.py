import logging
import re
import typing as T
from collections import abc
from copy import deepcopy

from unidecode import unidecode_expect_ascii  # type: ignore

from nominally import config

logger = logging.getLogger("nominally")

Pieces = T.List[str]
PiecesList = T.List[Pieces]
PiecesDict = T.Dict[str, Pieces]

if T.TYPE_CHECKING:
    MappingBase = T.Mapping[str, str]
else:
    MappingBase = abc.Mapping


class Name(MappingBase):
    """A human name, broken down into individual components."""

    _keys = ["title", "first", "middle", "last", "suffix", "nickname"]

    def __init__(self, raw: str = "") -> None:
        self._raw = raw
        print("raw  ", self._raw)
        pieceslist, work = self._pre_process(self._raw)
        pieceslist, work["title"] = self._extract_title(pieceslist)
        pieceslist, work["suffix"] = self._extract_suffixes(pieceslist)
        comma_sep_pieceslist = self._remove_numbers(pieceslist)
        # print("work   ", work)
        # print("pl     ", comma_sep_pieceslist)
        work.update(self._lfm_from_list(comma_sep_pieceslist))
        self._final = work
        print("final ", self._final)

        self._unparsable = not any(x for x in self.values() if x)
        if not self.parsable:
            logger.info('Unparsable: "%s" ', self._raw)

    @classmethod
    def _lfm_from_list(cls, pieceslist: PiecesList) -> PiecesDict:

        result: PiecesDict = {"first": [], "middle": [], "last": []}

        if not any(flatten_once(pieceslist)):
            return result  # return if empty

        # Last: take from front if a comma-separated value is there; otherwise from end
        if len(pieceslist) == 1:
            pieceslist[0] = cls._parse_pieces(pieceslist[0])
            result["last"] = [pieceslist[0].pop(-1)]
        else:
            result["last"] = pieceslist.pop(0)

        # Remove empties
        pieceslist[0] = [x for x in pieceslist[0] if x]
        pieceslist = [x for x in pieceslist if x]

        if not any(flatten_once(pieceslist)):
            return result

        if len(pieceslist) == 1:
            result["first"] = [pieceslist[0].pop(0)]
        else:
            result["first"] = pieceslist.pop(0)

        # Everything left is a middle name
        result["middle"] = flatten_once(pieceslist)

        return result

    @classmethod
    def _pre_process(cls, s: str) -> T.Tuple[PiecesList, PiecesDict]:
        logger.debug(repr(s))
        working: PiecesDict = {k: [] for k in cls._keys}
        s = str(s).lower()
        s, working = cls._parse_nicknames(s, working)
        s = cls._clean_input(s)
        logger.debug(repr(s))
        pieceslist = cls._string_to_pieceslist(s)
        return pieceslist, working

    @staticmethod
    def _clean_input(s: str) -> str:
        """Clean this string; assume that any nicknames have already been removed."""
        s = unidecode_expect_ascii(s).lower()
        s = re.sub(r'"|`', "'", s)  # convert all quotes/ticks to single quotes
        s = re.sub(r";|:|,", ", ", s)  # convert : ; , to , with spacing
        s = re.sub(r"[-_/\\:]+", "-", s)  # convert _ / \ - : to single hyphen
        s = re.sub(r"[^-\sa-z0-9',]+", "", s)  # drop most all excluding - ' ,
        s = re.sub(r"\s+", " ", s)  # condense all whitespace to single space
        s = s.strip("- ")  # drop leading/trailing hyphens and spaces
        return s

    @staticmethod
    def _string_to_pieceslist(remaining: str) -> PiecesList:
        pieces = re.split(r"\s*,\s*", remaining)
        return [x.split() for x in pieces if x]

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
    def _extract_title(pieceslist: PiecesList) -> T.Tuple[PiecesList, Pieces]:
        outgoing: PiecesList = []
        while pieceslist:
            next_cluster = pieceslist.pop(0)

            first_word, *remainder = next_cluster
            if is_title(first_word):
                outgoing = outgoing + [remainder] + pieceslist
                return outgoing, [first_word]

            outgoing.append(next_cluster)
        return outgoing, []

    @staticmethod
    def _extract_suffixes(
        incoming: PiecesList, min_names: int = 2
    ) -> T.Tuple[PiecesList, Pieces]:

        out_pl: PiecesList = []
        out_suffixes: Pieces = []
        banking: Pieces = []

        queued = deepcopy(incoming)  # avoid popping side effects
        while queued:
            handling = queued.pop()
            while handling:
                banking = []
                if (
                    sum(len(x) for x in (handling, banking))
                    + sum(count_words(pl) for pl in (queued, out_pl))
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

        return (out_pl, out_suffixes)

    @staticmethod
    def _remove_numbers(pieces: PiecesList) -> PiecesList:
        no_numbers = [[re.sub(r"\d", "", x) for x in piece] for piece in pieces]
        return remove_falsey(no_numbers)

    @classmethod
    def _parse_pieces(cls, pieces: Pieces) -> Pieces:
        """
        Split list of pieces down to individual words and
            - join on conjuctions if appropriate
            - add prefixes to last names if appropriate
        """
        # print("_parse_pieces inn", pieces)
        out_pieces = cls._break_down_to_words(pieces)
        out_pieces = cls._combine_conjunctions(out_pieces)
        out_pieces = cls._combine_prefixes(out_pieces)
        # print("_parse_pieces out", out_pieces)
        return out_pieces

    @staticmethod
    def _break_down_to_words(parts: Pieces) -> Pieces:
        result = parts
        return result

    @staticmethod
    def _combine_conjunctions(words: Pieces) -> Pieces:
        if len(words) < 4:
            return words

        result: Pieces = []
        queued = deepcopy(words)  # avoid popping side effects
        while queued:
            word = queued.pop(-1)
            if is_conjunction(word) and result and queued:
                clause = [queued.pop(-1), word, result.pop(0)]
                word = " ".join(clause)
            result.insert(0, word)
        return result

    @staticmethod
    def _combine_prefixes(pieces: Pieces) -> Pieces:
        if len(pieces) < 3:
            return pieces

        result: PiecesList = [[]]
        queued = deepcopy(pieces)  # avoid popping side effects
        while queued:
            word = queued.pop(-1)
            # A prefix goes in the first box; otherwise make a new box
            if is_prefix(word):
                result[0].insert(0, word)
            else:
                # Otherwise make a new box
                result.insert(0, [word])
        final_pieces: Pieces = [" ".join(piece) for piece in result if piece]
        return final_pieces

    def __eq__(self, other: T.Any) -> bool:
        try:
            return dict(self) == dict(other) and self.parsable
        except (ValueError, TypeError):
            return NotImplemented

    def __getattr__(self, name: str) -> T.Any:
        """
        Provides attribute access to all of Name._keys (by way of __iter__()
        for the keys and __getitem__() for the value).
        """
        if name in self.keys():
            return self[name]
        return self.__getattribute__(name)

    def __getitem__(self, key: str) -> T.Any:
        return " ".join(self._final[key]) or ""

    def __len__(self) -> int:
        return len(self._final)

    def __iter__(self) -> T.Iterator[str]:
        return iter(self._keys)

    def __repr__(self) -> str:
        if self.parsable:
            text = str(dict(self))
        else:
            text = "Unparsable"
        return f"{self.__class__.__name__}({text})"

    def __str__(self) -> str:
        string_parts = [
            f"{self.last},",
            self.title,
            self.first,
            f"({self.nickname})" if self.nickname else "",
            self.middle,
            self.suffix,
        ]
        joined = " ".join(p for p in string_parts if p)
        return re.sub(r"\s+", " ", joined).strip()

    # API

    @property
    def parsable(self) -> bool:
        return not self._unparsable

    @property
    def raw(self) -> str:
        return self._raw

    def report(self) -> T.Dict[str, T.Any]:
        return {
            "raw": self.raw,
            "parsed": str(self),
            "list": list(self.values()),
            **dict(self),
        }


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


def flatten_once(nested_list: T.List[T.Any]) -> T.List[T.Any]:
    return [item for sublist in nested_list for item in sublist]


def remove_falsey(seq: T.List[T.Any]) -> T.List[T.Any]:
    if not isinstance(seq, list):
        return seq
    return [x for x in map(remove_falsey, seq) if x]
