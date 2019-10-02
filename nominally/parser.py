import functools
import re
import typing as T
from collections import abc

from unidecode import unidecode_expect_ascii

from nominally import config
from nominally.utilities import flatten_once, remove_falsy

Cluster = T.List[str]
Clusters = T.List[Cluster]

if T.TYPE_CHECKING:
    MappingBase = T.Mapping[str, str]
else:
    MappingBase = abc.Mapping


def word_count_bouncer(minimum: int) -> T.Callable[[T.Any], T.Any]:
    """
    Decorate only class/instance methods, enforce word count on first real arg.

    If there are too few (less than minimum) words, return the arguments.
    """

    WordContainer = T.Union[str, Cluster, Clusters]

    def decorator_bouncer(
        func: T.Callable[[T.Any, WordContainer], WordContainer]
    ) -> T.Callable[[T.Any, WordContainer], WordContainer]:
        """Return countable instead of func(countable) if too few words."""

        @functools.wraps(func)
        def wrapper_bouncer(obj: T.Any, countable: WordContainer) -> WordContainer:
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
        self.detail: T.Dict[str, Cluster] = {k: [] for k in self._keys}

        s = self._pre_clean(self.raw)
        s = self._pre_process(s)
        s = self.clean(s)
        self._cleaned = self._archive_cleaned(s)
        self._process(s)
        self._post_process()
        self._final = self._post_clean()

    @staticmethod
    def _pre_clean(s: str) -> str:
        """Minimal possible pre-clean

        Still, e.g., allowing nickname extraction.
        """
        s = str(s)
        s = unidecode_expect_ascii(s)
        s = s.lower()
        return s

    def _pre_process(self, s: str) -> str:
        """Pull pieces that need to/can be processed from a string first."""
        s = self._sweep_nicknames(s)
        s = self._sweep_suffixes(s)
        s = self._sweep_junior(s)
        self.detail["nickname"] = self._clean_cluster(self.detail["nickname"])
        self.detail["suffix"] = self._clean_cluster(
            self.detail["suffix"], condense=True
        )
        return s

    @classmethod
    def clean(cls, s: str, *, condense: bool = False, final: bool = False) -> str:
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
        ]
        if final:
            cleaning_subs.append((r"[^a-z0-9- \)\()]", ""))
        for pattern, repl in cleaning_subs:
            s = re.sub(pattern, repl, s)
        s = cls.strip_pointlessness(s)

        if not re.search(r"[a-z]", s):
            return ""
        return s

    @staticmethod
    def strip_pointlessness(s: str) -> str:
        return s.strip("-, |")

    def _archive_cleaned(self, s: str) -> T.Set[str]:
        """Return a handy representation of cleaned string(s) as a set."""
        result = {s}
        result.update(*(tuple(x) for x in self.detail.values() if x))
        return result

    def _process(self, preprocessed_str: str) -> None:
        """Primary processing of clusters into extracted name parts."""
        clusters = self._string_to_clusters(preprocessed_str)
        clusters = self._extract_title(clusters)
        clusters = self._remove_numbers(clusters)
        clusters = self._grab_junior(clusters)
        self._extract_last_first_middle(clusters)

    def _post_process(self) -> None:
        """Any followup processes once all name parts have been extracted."""
        self.detail["suffix"].sort()

    @word_count_bouncer(minimum=3)
    def _sweep_suffixes(self, s: str) -> str:
        """Extract all possible (most) suffixes."""
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
        """First pass at 'junior' via regex from string."""
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

    @staticmethod
    def _string_to_clusters(remaining: str) -> Clusters:
        """Break a string into clusters by commas.

        I.e., 'piranha, dinsdale j' ->  [['piranha'], ['dinsdale', 'j']]
        """
        cluster = re.split(r"\s*,\s*", remaining)
        return [x.split() for x in cluster if x]

    def _extract_title(self, clusters: Clusters) -> Clusters:
        outgoing: Clusters = []
        while clusters:
            next_cluster = clusters.pop(0)

            first_word, *remainder = next_cluster
            if first_word in config.TITLES:
                outgoing = outgoing + [remainder] + clusters
                self.detail["title"] = [first_word]
                return outgoing

            outgoing.append(next_cluster)
        self.detail["title"] = []
        return outgoing

    @staticmethod
    def _remove_numbers(cluster: Clusters) -> Clusters:
        """Clear out all numbers.

        Intended to be applied following primary generational suffix extraction.
        """
        no_numbers = [[re.sub(r"\d", "", x) for x in word] for word in cluster]
        return remove_falsy(no_numbers)

    def _post_clean(self) -> T.Dict[str, Cluster]:
        return {k: self._clean_cluster(self.detail[k]) for k in self._keys}

    @classmethod
    def _clean_cluster(cls, cluster: Cluster, condense: bool = False) -> Cluster:
        """Clean the string of each token in a cluster."""
        cleaned = [cls.clean(s, condense=condense, final=True) for s in cluster]
        return [s for s in cleaned if s]

    @word_count_bouncer(minimum=3)
    def _grab_junior(self, clusters: Clusters) -> Clusters:
        """
        Extract "junior" as suffix unless
        - there is already a generational suffix
        - junior is the first word of the only cluster (e.g. 'junior x. smith')
        - junior is the first word of a multi-token multi-cluster
            e.g. leave as first 'smith, junior x'
                 leave as first 'barnes-smith, junior james'
                 take as suffix 'jake smith, junior'
        """

        if self._has_generational:
            return clusters

        if "junior" not in flatten_once(clusters):
            return clusters

        first_word_only_cluster = len(clusters) == 1 and clusters[0][0] == "junior"
        if first_word_only_cluster:
            return clusters

        first_word_in_likely_first_name = (
            len(clusters) == 2 and len(clusters[1]) > 1 and clusters[1][0] == "junior"
        )
        if first_word_in_likely_first_name:
            return clusters

        self.detail["suffix"].append("jr")
        return self._remove_from_clusters(clusters, "junior")

    @staticmethod
    def _remove_from_clusters(clusters: Clusters, s: str) -> Clusters:
        """Drop all strings from clusters that are equal to s"""
        return [[x for x in cluster if x != s] for cluster in clusters]

    def _extract_last_first_middle(self, clusters: Clusters) -> None:
        """Sequentially remove last name, first name, and collapse to middles"""
        clusters = self._extract_last(remove_falsy(clusters))
        clusters = self._extract_first(remove_falsy(clusters))
        self.detail["middle"] = flatten_once(clusters)

    @word_count_bouncer(1)
    def _extract_first(self, clusters: Clusters) -> Clusters:
        """
        Remove and return the first name from a prepared list of cluster

        If only one cluster remains, take its leftmost word;
        if more than one, take the leftmost cluster.
        """
        if len(clusters) == 1:
            self.detail["first"] = [clusters[0].pop(0)]
            return clusters
        self.detail["first"] = clusters.pop(0)
        return clusters

    @word_count_bouncer(1)
    def _extract_last(self, clusters: Clusters) -> Clusters:
        """Remove and return the last name from a prepared list of cluster"""
        # First, move any partitioned last name into rightmost cluster
        if len(clusters) > 1:
            clusters = self._flip_last_name_to_right(clusters)
        # Now group words of the rightmost cluster and take the rightmost word
        clusters[-1] = self._cluster_words(clusters[-1])
        self.detail["last"] = [clusters[-1].pop(-1)]
        return clusters

    @classmethod
    def _flip_last_name_to_right(cls, clusters: Clusters) -> Clusters:
        """Set up extraction by moving a last name to rightmost position"""
        partitioned_last = " ".join(clusters.pop(0))
        clusters[-1].append(partitioned_last)
        return clusters

    @classmethod
    def _cluster_words(cls, cluster: Cluster) -> Cluster:
        """
        Split list of cluster down to individual words and
            - join on conjuctions if appropriate
            - add prefixes to last names if appropriate
        """
        cluster = cls._combine_conjunctions(cluster)
        cluster = cls._combine_rightmost_prefixes(cluster)
        return cluster

    @classmethod
    @word_count_bouncer(minimum=4)
    def _combine_conjunctions(cls, cluster: Cluster) -> Cluster:
        """Accept one conjunction at the end: `bob|steve|cortez y costa`"""
        *new_cluster, last_name_one, conj, last_name_two = cluster

        if conj not in config.CONJUNCTIONS:
            return cluster

        rightmost = " ".join((last_name_one, conj, last_name_two))
        new_cluster.append(rightmost)
        return new_cluster

    @classmethod
    @word_count_bouncer(minimum=3)
    def _combine_rightmost_prefixes(cls, cluster: Cluster) -> Cluster:
        """Work right-to-left through cluster, joining up prefixes of rightmost"""
        result: Clusters = []

        for word in reversed(cluster):
            if len(result) > 1 or word not in config.PREFIXES:
                result.insert(0, [word])
                continue
            if not result:
                result = [[]]
            result[0].insert(0, word)

        return [" ".join(cluster) for cluster in result if cluster]

    def __eq__(self, other: T.Any) -> bool:
        """If Name is parsable and object dicts are identical, consider it equal."""
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
        """Implement Name dict to return strings"""
        return " ".join(self._final[key]) or ""

    def __len__(self) -> int:
        """Implement Name dict to return strings"""
        return len(self._keys)

    def __iter__(self) -> T.Iterator[str]:
        """Implement Name dict to return strings"""
        return iter(self._keys)

    def __repr__(self) -> str:
        if self.parsable:
            text = str(dict(self))
        else:
            text = "Unparsable"
        return f"{self.__class__.__name__}({text})"

    def __str__(self) -> str:
        """Output format: "last, title first middle suffix (nickname)"

        - "organs, mr harry x, jr (snapper)"
        - "organs, mr harry x, jr"
        - "organs, mr harry x"
        - "organs, harry x"
        - "organs, harry"
        - etc.
        """
        string_parts = [
            f"{self.last},",
            self.title,
            self.first,
            f"({self.nickname})" if self.nickname else "",
            self.middle,
            self.suffix,
        ]
        joined = " ".join(p for p in string_parts if p)
        return self.strip_pointlessness(joined)

    # API

    @property
    def parsable(self) -> bool:
        """Return true if any valid name values were created."""
        return any(x for x in self.values() if x)

    @property
    def raw(self) -> str:
        """Return the original input string."""
        return self._raw

    @property
    def cleaned(self) -> T.Set[str]:
        """Return some set of cleaned string parts."""
        return self._cleaned

    def report(self) -> T.Dict[str, T.Any]:
        """Return a more-or-less complete parsing dict."""
        return {
            "raw": self.raw,
            "cleaned": self.cleaned,
            "parsed": str(self),
            "list": list(self.values()),
            **dict(self),
        }
