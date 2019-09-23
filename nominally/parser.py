import functools
import re
import typing as T
from collections import abc

from unidecode import unidecode_expect_ascii  # type: ignore

from nominally import config
from nominally.utilities import flatten_once, remove_falsy

Pieces = T.List[str]
PiecesList = T.List[Pieces]
WordCountable = T.Union[str, Pieces, PiecesList]

if T.TYPE_CHECKING:
    MappingBase = T.Mapping[str, str]
else:
    MappingBase = abc.Mapping


def word_count_bouncer(minimum: int) -> T.Callable[[T.Any], T.Any]:
    """
    Decorate only class/instance methods, enforce word count on first real arg.

    If there are too few (less than minimum) words, return the arguments.
    """

    def decorator_bouncer(
        func: T.Callable[[T.Any, WordCountable], WordCountable]
    ) -> T.Callable[[T.Any, WordCountable], WordCountable]:
        @functools.wraps(func)
        def wrapper_bouncer(obj: T.Any, countable: WordCountable) -> WordCountable:

            checklist: T.List[T.Any]
            if not countable:
                return countable
            if isinstance(countable, str):
                checklist = countable.split()
            elif isinstance(countable[0], str):
                checklist = countable
            else:
                checklist = flatten_once(countable)
            wordlist = [s for s in checklist if re.search("[a-z]", s)]
            if len(wordlist) < minimum:
                return countable
            return func(obj, countable)

        return wrapper_bouncer

    return decorator_bouncer


class Name(MappingBase):
    """A personal name, separated and simplified into component parts."""

    _keys = ["title", "first", "middle", "last", "suffix", "nickname"]
    # https://github.com/vaneseltine/nominally/issues/47
    __slots__ = _keys + ["_raw", "_has_generational", "detail", "_final", "_cleaned"]

    def __init__(self, raw: str = "") -> None:

        self._raw = raw
        self._has_generational = False
        self.detail: T.Dict[str, Pieces] = {k: [] for k in self._keys}

        s = self._pre_clean(self.raw)
        s = self._pre_process(s)
        s = self.clean(s)
        self._cleaned = self._archive_cleaned(s)
        self._process(s)
        self._post_process()
        self._final = self._post_clean()

    @staticmethod
    def _pre_clean(s: str) -> str:
        return unidecode_expect_ascii(str(s)).lower()  # type: ignore

    def _pre_process(self, s: str) -> str:
        s = self._sweep_nicknames(s)
        s = self._sweep_suffixes(s)
        s = self._sweep_junior(s)
        self.detail["nickname"] = self._clean_pieces(self.detail["nickname"])
        self.detail["suffix"] = self._clean_pieces(self.detail["suffix"], condense=True)
        return s

    def _archive_cleaned(self, s: str) -> T.Set[str]:
        result = {s}
        result.update(*(tuple(x) for x in self.detail.values() if x))
        return result

    @staticmethod
    def _string_to_pieceslist(remaining: str) -> PiecesList:
        pieces = re.split(r"\s*,\s*", remaining)
        return [x.split() for x in pieces if x]

    def _process(self, preprocessed_str: str) -> None:
        pieceslist = self._string_to_pieceslist(preprocessed_str)
        pieceslist = self._extract_title(pieceslist)
        pieceslist = self._remove_numbers(pieceslist)
        pieceslist = self._grab_junior(pieceslist)
        self._extract_last_first_middle(pieceslist)

    def _post_process(self) -> None:
        self.detail["suffix"].sort()

    @staticmethod
    def clean(s: str, *, condense: bool = False, final: bool = False) -> str:
        """Clean this string to the simplest possible representation (but no simpler).

        .. note::

            Assumes that any nicknames have already been removed,
            along with anything else that would depend on special
            characters (other than commas).
        """
        whitespace_out = "" if condense else " "
        cleaning_subs = [
            (r"(\s*(;|:|,))+", ", "),  # convert : ; , to , with spacing
            (r"\.\s*", ". "),  # reduce/add space after each .
            (r"[-_/\\:]+", "-"),  # convert _ / \ - : to single hyphen
            (r"[^-\sa-z0-9,]+", ""),  # drop most all excluding -  , .
            (r"\s+", whitespace_out),  # condense all whitespace groups
            (r"^[-, ]+", ""),  # lstrip hyphens, spaces, commas
            (r"[-, ]+$", ""),  # rstrip hyphens, spaces, commas
        ]
        if final:
            cleaning_subs.append((r"[^a-z0-9- \)\()]", ""))
        for pattern, repl in cleaning_subs:
            s = re.sub(pattern, repl, s)

        if not re.search(r"[a-z]", s):
            return ""
        return s

    @word_count_bouncer(minimum=3)
    def _sweep_suffixes(self, s: str) -> str:
        for pat, generational in config.SUFFIX_PATTERNS.items():
            if not pat.search(s):
                continue
            new_suffixes = pat.findall(s)
            if generational:
                self._has_generational = True
            self.detail["suffix"] += new_suffixes
            s = pat.sub("", s)
        return s

    @word_count_bouncer(minimum=3)
    def _sweep_junior(self, s: str) -> str:
        if self._has_generational:
            return s
        new_s = config.JUNIOR_PATTERN.sub(", ", s)
        if new_s != s:
            self.detail["suffix"].append("jr")
        return new_s

    @word_count_bouncer(minimum=3)
    def _sweep_nicknames(self, s: str) -> str:
        """
        The content of parenthesis or quotes in the name will be added to the
        nicknames list. This happens before any other processing of the name.

        Single quotes cannot span white space characters and must border
        white space to allow for quotes in names like O'Connor and Kawai'ae'a.
        Double quotes and parenthesis can span white space.
        """

        for pattern in config.NICKNAME_PATTERNS:
            hit = pattern.findall(s)
            if hit:
                self.detail["nickname"] += hit
                s = pattern.sub("", s)
        return s

    def _extract_title(self, pieceslist: PiecesList) -> PiecesList:
        outgoing: PiecesList = []
        while pieceslist:
            next_cluster = pieceslist.pop(0)

            first_word, *remainder = next_cluster
            if first_word in config.TITLES:
                outgoing = outgoing + [remainder] + pieceslist
                self.detail["title"] = [first_word]
                return outgoing

            outgoing.append(next_cluster)
        self.detail["title"] = []
        return outgoing

    @staticmethod
    def _remove_numbers(pieces: PiecesList) -> PiecesList:
        no_numbers = [[re.sub(r"\d", "", x) for x in piece] for piece in pieces]
        return remove_falsy(no_numbers)

    def _post_clean(self) -> T.Dict[str, Pieces]:
        return {k: self._clean_pieces(self.detail[k]) for k in self._keys}

    @classmethod
    def _clean_pieces(cls, pieces: Pieces, condense: bool = False) -> Pieces:
        cleaned = [cls.clean(s, condense=condense, final=True) for s in pieces]
        return [s for s in cleaned if s]

    @word_count_bouncer(minimum=3)
    def _grab_junior(self, pieceslist: PiecesList) -> PiecesList:
        """
        Extract "junior" as suffix unless
        - there is already a generational suffix
        - junior is the first word of the only piece (e.g. 'junior x. smith')
        - junior is the first word of a multi-part multi-piece
            e.g. leave as first 'smith, junior x'
                 leave as first 'barnes-smith, junior james'
                 take as suffix 'jake smith, junior'
        """

        if self._has_generational:
            return pieceslist

        if "junior" not in flatten_once(pieceslist):
            return pieceslist

        first_word_only_cluster = len(pieceslist) == 1 and pieceslist[0][0] == "junior"
        if first_word_only_cluster:
            return pieceslist

        first_word_in_likely_first_name = (
            len(pieceslist) == 2
            and len(pieceslist[1]) > 1
            and pieceslist[1][0] == "junior"
        )
        if first_word_in_likely_first_name:
            return pieceslist

        self.detail["suffix"].append("jr")
        return self._remove_from_pieceslist(pieceslist, "junior")

    @staticmethod
    def _remove_from_pieceslist(pieceslist: PiecesList, s: str) -> PiecesList:
        return [[x for x in piece if x != s] for piece in pieceslist]

    def _extract_last_first_middle(self, pieceslist: PiecesList) -> None:
        pieceslist = self._extract_last(remove_falsy(pieceslist))
        pieceslist = self._extract_first(remove_falsy(pieceslist))
        self.detail["middle"] = flatten_once(pieceslist)

    @word_count_bouncer(1)
    def _extract_first(self, pieceslist: PiecesList) -> PiecesList:
        """
        Remove and return the first name from a prepared list of pieces

        If only one piece remains, take its leftmost word;
        if more than one, take the leftmost piece.
        """
        if len(pieceslist) == 1:
            self.detail["first"] = [pieceslist[0].pop(0)]
            return pieceslist
        self.detail["first"] = pieceslist.pop(0)
        return pieceslist

    @word_count_bouncer(1)
    def _extract_last(self, pieceslist: PiecesList) -> PiecesList:
        """Remove and return the last name from a prepared list of pieces"""
        # First, move any partitioned last name into rightmost piece
        if len(pieceslist) > 1:
            pieceslist = self.flip_last_name_to_right(pieceslist)
        # Now group words of the rightmost piece and take the rightmost cluster
        pieceslist[-1] = self._cluster_words(pieceslist[-1])
        self.detail["last"] = [pieceslist[-1].pop(-1)]
        return pieceslist

    @classmethod
    def flip_last_name_to_right(cls, pieceslist: PiecesList) -> PiecesList:
        partitioned_last = " ".join(pieceslist.pop(0))
        pieceslist[-1].append(partitioned_last)
        return pieceslist

    @classmethod
    def _cluster_words(cls, pieces: Pieces) -> Pieces:
        """
        Split list of pieces down to individual words and
            - join on conjuctions if appropriate
            - add prefixes to last names if appropriate
        """
        pieces = cls._combine_conjunctions(pieces)
        pieces = cls._combine_rightmost_prefixes(pieces)
        return pieces

    @classmethod
    @word_count_bouncer(minimum=4)
    def _combine_conjunctions(cls, pieces: Pieces) -> Pieces:
        *new_pieces, last_name_one, conj, last_name_two = pieces

        if conj not in config.CONJUNCTIONS:
            return pieces

        rightmost = " ".join((last_name_one, conj, last_name_two))
        new_pieces.append(rightmost)
        return new_pieces

    @classmethod
    @word_count_bouncer(minimum=3)
    def _combine_rightmost_prefixes(cls, pieces: Pieces) -> Pieces:
        """Work right-to-left through pieces, joining up prefixes of rightmost"""
        result: PiecesList = []

        for word in reversed(pieces):
            if len(result) > 1 or word not in config.PREFIXES:
                result.insert(0, [word])
                continue
            if not result:
                result = [[]]
            result[0].insert(0, word)

        return [" ".join(piece) for piece in result if piece]

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
        return len(self._keys)

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
            self.middle,
            self.suffix,
        ]
        joined = " ".join(p for p in string_parts if p)
        prepared = self.clean(joined)
        if self.nickname:
            prepared += f" ({self.nickname})"
        return prepared

    # API

    @property
    def parsable(self) -> bool:
        return any(x for x in self.values() if x)

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
