import re
import typing as T
from collections import abc, defaultdict
from copy import deepcopy

from unidecode import unidecode_expect_ascii  # type: ignore

from nominally import config

Pieces = T.List[str]
PiecesList = T.List[Pieces]
PiecesDefaultDict = T.DefaultDict[str, Pieces]

if T.TYPE_CHECKING:
    MappingBase = T.Mapping[str, str]
else:
    MappingBase = abc.Mapping


class Name(MappingBase):
    """A human name, broken down into individual components."""

    _keys = ["title", "first", "middle", "last", "suffix", "nickname"]

    def __init__(self, raw: str = "") -> None:
        self._raw = raw
        pieceslist, work = self._pre_process(self._raw)
        pieceslist, work["title"] = self._extract_title(pieceslist)
        pieceslist = self._remove_numbers(pieceslist)
        pieceslist, work = self._grab_junior(pieceslist, work)
        work = self._lfm_from_list(pieceslist, work)
        self._final = self._get_final(work)
        self._cleaned = set(work["cleaned"])

        self._unparsable = not any(x for x in self.values() if x)
        if not self.parsable:
            print('Unparsable: "%s" ', self._raw)

    @classmethod
    def _pre_process(cls, s: str) -> T.Tuple[PiecesList, PiecesDefaultDict]:
        # print(repr(s))
        working: PiecesDefaultDict = defaultdict(list, {k: [] for k in cls._keys})

        s = str(s).lower()
        s, working = cls._sweep_nicknames(s, working)
        s, working = cls._sweep_suffixes(s, working)
        s = cls._clean_input(s)
        # print(repr(s))

        pieceslist = cls._string_to_pieceslist(s)
        working["cleaned"] = [s]
        for k in [*cls._keys, "generational"]:
            if working[k]:
                working["cleaned"] += working[k]
        return pieceslist, working

    @staticmethod
    def _clean_input(s: str, condense: bool = False) -> str:
        """Clean this string to the simplest possible representation (but no simpler).

        Assumes that any nicknames have already been removed or anything else that
        would depend on special characters."""
        s = unidecode_expect_ascii(s).lower()
        s = re.sub(r'"|`', "'", s)  # convert all quotes/ticks to single quotes
        s = re.sub(r"(\s*(;|:|,))+", ", ", s)  # convert : ; , to , with spacing
        s = re.sub(r"\.\s*", ". ", s)  # reduce/add space after each .
        s = re.sub(r"[-_/\\:]+", "-", s)  # convert _ / \ - : to single hyphen
        s = re.sub(r"[^-\sa-z0-9',]+", "", s)  # drop most all excluding - ' , .
        s = re.sub(r"\s+", " ", s)  # condense all whitespace groups to a single space
        s = s.strip("- ")  # drop leading/trailing hyphens and spaces
        if condense:
            s = s.replace(" ", "")
        return s

    @classmethod
    def _sweep_suffixes(
        cls, s: str, working: PiecesDefaultDict
    ) -> T.Tuple[str, PiecesDefaultDict]:
        # print(f"_sweep_suffixes in {s} {working}")
        for pat, generational in config.SUFFIX_PATTERNS.items():
            # print(f"searching {pat}")
            if not pat.search(s):
                continue
            # print(f"found {pat} {s}")
            new_suffix = [cls._clean_input(x, condense=True) for x in pat.findall(s)]
            if generational:
                working["generational"] += new_suffix
            else:
                working["suffix"] += new_suffix
            s = pat.sub("", s)
            # print(f"yay, {pat}, {repr(s)}")
        # Remove any comma-bracketed 'junior's
        s, working = cls._sweep_junior(s, working)
        s = cls._clean_input(s)
        return s, working

    @classmethod
    def _sweep_junior(
        cls, s: str, working: PiecesDefaultDict
    ) -> T.Tuple[str, PiecesDefaultDict]:
        if working["generational"]:
            print("MOOOOO")
            return s, working
        if not config.JUNIOR_PATTERN.findall(s):
            return s, working
        if len(config.WORD_FINDER.findall(s)) < 3:
            return s, working

        s = config.JUNIOR_PATTERN.sub(", ", s)
        working["generational"].insert(0, "junior")

        return s, working

    @classmethod
    def _sweep_nicknames(
        cls, s: str, working: PiecesDefaultDict
    ) -> T.Tuple[str, PiecesDefaultDict]:
        """
        The content of parenthesis or quotes in the name will be added to the
        nicknames list. This happens before any other processing of the name.

        Single quotes cannot span white space characters and must border
        white space to allow for quotes in names like O'Connor and Kawai'ae'a.
        Double quotes and parenthesis can span white space.
        """

        for pattern in config.NICKNAME_PATTERNS:
            if pattern.search(s):
                working["nickname"] += [cls._clean_input(x) for x in pattern.findall(s)]
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
    def _remove_numbers(pieces: PiecesList) -> PiecesList:
        no_numbers = [[re.sub(r"\d", "", x) for x in piece] for piece in pieces]
        return remove_falsey(no_numbers)

    @staticmethod
    def _string_to_pieceslist(remaining: str) -> PiecesList:
        pieces = re.split(r"\s*,\s*", remaining)
        return [x.split() for x in pieces if x]

    @classmethod
    def _get_final(cls, work: PiecesDefaultDict) -> T.Dict[str, Pieces]:
        work["suffix"] += work["generational"]
        final: T.Dict[str, Pieces] = {k: cls.final_clean(work[k]) for k in cls._keys}
        return final

    @staticmethod
    def final_clean(pieces: Pieces) -> Pieces:
        return [s.replace(".", "") for s in pieces]

    @classmethod
    def _grab_junior(
        cls, pieceslist: PiecesList, work: PiecesDefaultDict
    ) -> T.Tuple[PiecesList, PiecesDefaultDict]:
        checklist = flatten_once(pieceslist)
        if "junior" not in checklist:
            return pieceslist, work
        if len(checklist) < 3:
            return pieceslist, work
        if work["generational"]:
            return pieceslist, work

        if pieceslist[-1][-1] == "junior":
            pieceslist[-1].remove("junior")
            work["generational"].insert(0, "junior")
            return pieceslist, work

        first_name_cluster_index = 0 if len(pieceslist) == 1 else 1

        junior_index = pieceslist[first_name_cluster_index].index("junior")

        if junior_index:
            pieceslist[first_name_cluster_index].remove("junior")
            work["generational"].insert(0, "junior")

        return pieceslist, work

    @classmethod
    def _lfm_from_list(
        cls, pieceslist: PiecesList, work: PiecesDefaultDict
    ) -> PiecesDefaultDict:
        # Remove empties and finish if nothing of substance remains
        pieceslist = remove_falsey(pieceslist)
        if not any(flatten_once(pieceslist)):
            return work  # return if empty

        # If we have only one piece left, group words and take its rightmost cluster
        if len(pieceslist) == 1:
            pieceslist[0] = cls._cluster_words(pieceslist[0])
            work["last"] = [pieceslist[0].pop(-1)]
        # Otherwise, meaning multiple pieces remain: take its rightmost piece
        else:
            work["last"] = pieceslist.pop(0)
        # print("-------------------------------------------", pieceslist)

        # Remove empties and finish if nothing of substance remains
        pieceslist = remove_falsey(pieceslist)
        if not any(flatten_once(pieceslist)):
            return work

        # If only one piece remains, take its leftmost word
        if len(pieceslist) == 1:
            work["first"] = [pieceslist[0].pop(0)]
        # Otherwise, meaning multiple pieces remain: take its leftmost piece
        else:
            work["first"] = pieceslist.pop(0)

        # Everything remaining is a middle name
        work["middle"] = flatten_once(pieceslist)
        return work

    @classmethod
    def _cluster_words(cls, pieces: Pieces) -> Pieces:
        """
        Split list of pieces down to individual words and
            - join on conjuctions if appropriate
            - add prefixes to last names if appropriate
        """
        out_pieces = cls._break_down_to_words(pieces)
        out_pieces = cls._combine_conjunctions(out_pieces)
        out_pieces = cls._combine_rightmost_prefixes(out_pieces)
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
    def _combine_rightmost_prefixes(pieces: Pieces) -> Pieces:
        if len(pieces) < 3:
            return pieces
        # print(f"---- combine in {pieces}")
        result: PiecesList = []
        while pieces:
            word = pieces.pop(-1)
            # Make a new box
            if not is_prefix(word):
                result.insert(0, [word])

                if len(result) > 1:
                    # print("collapse res", result, pieces)
                    result = [[s] for s in pieces] + result
                    # print("collapse res", result, pieces)
                    break
                else:
                    continue

            # A prefix goes in the first box
            if not result:
                result = [[]]
            result[0].insert(0, word)

        # print(f"---- combine out {result}")
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

    @property
    def cleaned(self) -> T.Set[str]:
        return self._cleaned

    def report(self) -> T.Dict[str, T.Any]:
        return {
            "raw": self.raw,
            "cleaned": self.cleaned,
            "parsed": str(self),
            "list": list(self.values()),
            **dict(self),
        }


def is_title(value: str) -> bool:
    return value in config.TITLES


def is_conjunction(piece: str) -> bool:
    return piece.lower() in config.CONJUNCTIONS


def is_prefix(piece: str) -> bool:
    return piece in config.PREFIXES


def flatten_once(nested_list: T.List[T.Any]) -> T.List[T.Any]:
    return [item for sublist in nested_list for item in sublist]


def remove_falsey(seq: T.List[T.Any]) -> T.List[T.Any]:
    if not isinstance(seq, list):
        return seq
    return [x for x in map(remove_falsey, seq) if x]
