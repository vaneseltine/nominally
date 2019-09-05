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

    def __init__(self, full_name=""):
        self.original = full_name
        self._full_name = self.original.lower()

        self.title_list = []
        self.first_list = []
        self.middle_list = []
        self.last_list = []
        self.suffix_list = []
        self.nickname_list = []

        self.pre_process()
        self.parse_full_name()
        self.post_process()

    def __len__(self):
        return len([v for k, v in dict(self).items() if v])

    def __eq__(self, other):
        if self.unparsable:
            return False
        return str(self).lower() == str(other).lower()

    def __getitem__(self, key):
        if key not in self.keys():
            try:
                true_key = self.keys()[key]
            except TypeError:
                raise KeyError(key)
            return self[true_key]
        return getattr(self, key)

    def __str__(self):
        s = " ".join(v for k, v in dict(self).items() if v and k != "nickname")
        if self.nickname:
            s += f" ({self.nickname})"
        return s

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
                self.nickname_list += [x for x in pattern.findall(self._full_name)]
                logger.debug(f"{pattern}, {self.nickname_list}")
                self._full_name = pattern.sub("", self._full_name)

    def thoroughly_clean(self):
        self._full_name = clean_input(self._full_name)

    def make_single_name_last(self):
        """
        If there are only two parts and one is a title, assume it's a last name
        instead of a first name. e.g. Mr. Johnson.
        """
        if self.title and len(self) == 2:
            self.first_list, self.last_list = self.last_list, self.first_list

    def parse_full_name(self):
        """

        The main parse method for the parser. This method is run upon
        assignment to the :py:attr:`full_name` attribute or instantiation.

        Basic flow is to hand off to :py:func:`pre_process` to handle
        nicknames. It then splits on commas and chooses a code path depending
        on the number of commas.

        :py:func:`parse_pieces` then splits those parts on spaces and
        :py:func:`join_on_conjunctions` joins any pieces next to conjunctions.
        """

        # break up full_name by commas
        parts = re.split(r"\s*,\s*", self._full_name)

        logger.debug("full_name: %s", self._full_name)
        logger.debug("parts: %s", parts)

        if len(parts) == 1:
            self.parse_v_no_commas(parts)

        else:
            # if all the end parts are suffixes and there is more than one piece
            # in the first part. (Suffixes will never appear after last names
            # only, and allows potential first names to be in suffixes, e.g.
            # "Johnson, Bart"
            if are_suffixes(parts[1].split(" ")) and len(parts[0].split(" ")) > 1:
                self.parse_v_suffix_comma(parts)
            else:
                self.parse_v_lastname_comma(parts)

        if self.unparsable:
            logger.info('Unparsable: "%s" ', self.original)

    def parse_v_suffix_comma(self, parts):
        # suffix comma:
        # * title first middle last [suffix], suffix [suffix] [, suffix]
        # *               parts0,          parts1..

        self.suffix_list += parts[1:]
        pieces = self.parse_pieces(parts[0].split(" "), additional_parts_count=0)
        logger.debug(f"parse_v_suffix_comma pieces: {pieces}")
        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None

            if is_title(piece) and (nxt or len(pieces) == 1) and not self.first:
                self.title_list.append(piece)
                continue
            if not self.first:
                self.first_list.append(piece)
                continue
            if are_suffixes(pieces[i + 1 :]):
                self.last_list.append(piece)
                self.suffix_list = pieces[i + 1 :] + self.suffix_list
                break
            if not nxt:
                self.last_list.append(piece)
                continue
            self.middle_list.append(piece)

    def parse_v_lastname_comma(self, parts):
        # lastname comma:
        # * last [suffix], title first middles[,] suffix [,suffix]
        # *     parts0      parts1,              parts2..
        pieces = self.parse_pieces(parts[1].split(" "), additional_parts_count=1)

        logger.debug(f"parse_v_lastname_comma pieces: {pieces}")

        # lastname part may have suffixes in it
        lastname_pieces = self.parse_pieces(
            parts[0].split(" "), additional_parts_count=1
        )
        for piece in lastname_pieces:
            # the first one is always a last name, even if it looks like
            # a suffix
            if is_suffix(piece) and self.last_list:
                self.suffix_list.append(piece)
            else:
                self.last_list.append(piece)

        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None

            if is_title(piece) and (nxt or len(pieces) == 1) and not self.first:
                self.title_list.append(piece)
                continue
            if not self.first:
                self.first_list.append(piece)
                continue
            if is_suffix(piece):
                self.suffix_list.append(piece)
                continue
            self.middle_list.append(piece)
        if len(parts) > 2:
            self.suffix_list += parts[2:]

    def parse_v_no_commas(self, parts):
        # ~ no commas, title first middle middle middle last suffix
        # ~           part[0
        pieces = self.parse_pieces(parts, additional_parts_count=0)
        logger.debug(f"parse_v_no_commas pieces: {pieces}")
        p_len = len(pieces)
        for i, piece in enumerate(pieces):
            try:
                nxt = pieces[i + 1]
            except IndexError:
                nxt = None

            # title must have a next piece, unless it's just a title
            if is_title(piece) and (nxt or p_len == 1) and not self.first:
                self.title_list.append(piece)
                continue
            if not self.first:
                if p_len == 1 and self.nickname:
                    self.last_list.append(piece)
                    continue
                self.first_list.append(piece)
                continue
            if are_suffixes(pieces[i + 1 :]) or (
                # if the next piece is the last piece and a roman
                # numeral but this piece is not an initial
                is_roman_numeral(nxt)
                and i == p_len - 2
                and not is_an_initial(piece)
            ):
                self.last_list.append(piece)
                self.suffix_list += pieces[i + 1 :]
                break
            if not nxt:
                self.last_list.append(piece)
                continue

            self.middle_list.append(piece)

    def parse_pieces(self, parts, additional_parts_count=0):
        """
        Split parts on spaces and remove commas, join on conjunctions and
        lastname prefixes. If parts have periods in the middle, try splitting
        on periods and check if the parts are titles or suffixes. If they are
        add to the constant so they will be found.

        :param list parts: name part strings from the comma split
        :param int additional_parts_count:

            if the comma format contains other parts, we need to know
            how many there are to decide if things should be considered a
            conjunction.
        :return: pieces split on spaces and joined on conjunctions
        :rtype: list
        """
        words = []
        # for part in self.properly_list_pieces(parts):
        logger.info(parts)
        for part in parts:
            for word in part.split():
                words.append(word)
        # words = [x for x in part.split(" ")]
        logger.debug(f"Incoming pieces: {words}")
        pieces = self.join_on_conjunctions(words)
        pieces = self.join_prefixes(pieces)
        logger.debug(f"Outgoing pieces: {pieces}")
        return pieces

    @staticmethod
    def join_on_conjunctions(words):
        """
        Join conjunctions to surrounding words. Title- and prefix-aware. e.g.:

            ['Mr.', 'and'. 'Mrs.', 'John', 'Doe'] ==>
                            ['Mr. and Mrs.', 'John', 'Doe']

            ['The', 'Secretary', 'of', 'State', 'Hillary', 'Clinton'] ==>
                            ['The Secretary of State', 'Hillary', 'Clinton']

        When joining titles, saves newly formed piece to the instance's titles
        constant so they will be parsed correctly later. E.g. after parsing the
        example names above, 'The Secretary of State' and 'Mr. and Mrs.' would
        be present in the titles constant set.


        """
        if len(words) <= 3:
            # No conjunctive mononyms
            return words

        conj_index = [i for i, piece in enumerate(words) if is_conjunction(piece)]
        logger.debug(f"conj_index: {conj_index}")

        for i in conj_index:
            new_piece = " ".join(words[i - 1 : i + 2])
            words[i - 1] = new_piece
            words.pop(i)
            words.pop(i)

        return words

    @staticmethod
    def join_prefixes(pieces):
        original = pieces
        logger.warning(pieces)
        if len(pieces) == 1:
            return pieces
        # join prefixes to following lastnames: ['de la Vega'], ['van Buren']
        prefixes = [x for x in pieces if is_prefix(x)]
        logger.debug(f"prefixes {prefixes}")
        for prefix in prefixes:
            try:
                i = pieces.index(prefix)
            except ValueError:
                # If the prefix is no longer in pieces, it's because it has been
                # combined with the prefix that appears right before (or before that when
                # chained together) in the last loop, so the index of that newly created
                # piece is the same as in the last loop, i==i still, and we want to join
                # it to the next piece.
                pass

            new_piece = ""

            # join everything after the prefix until the next prefix or suffix

            try:
                next_prefix = next(iter(filter(is_prefix, pieces[i + 1 :])))
                j = pieces.index(next_prefix)
                if j == i + 1:
                    # if there are two prefixes in sequence, join to the following piece
                    j += 1
                new_piece = " ".join(pieces[i:j])
                pieces = pieces[:i] + [new_piece] + pieces[j:]
            except StopIteration:
                try:
                    # if there are no more prefixes, look for a suffix to stop at
                    stop_at = next(iter(filter(is_suffix, pieces[i + 1 :])))
                    j = pieces.index(stop_at)
                    new_piece = " ".join(pieces[i:j])
                    pieces = pieces[:i] + [new_piece] + pieces[j:]
                except StopIteration:
                    # if there were no suffixes, nothing to stop at so join all
                    # remaining pieces
                    new_piece = " ".join(pieces[i:])
                    pieces = pieces[:i] + [new_piece]

        logger.debug("pieces: %s", pieces)
        if len(pieces) == 1:
            logger.debug("pieces: %s", pieces)
            logger.debug("Not expecting to arrive at only one piece; throwing back")
            pieces = original
        logger.warning(pieces)
        return pieces

    @property
    def title(self):
        return " ".join(self.title_list) or ""

    @property
    def first(self):
        return " ".join(self.first_list) or ""

    @property
    def middle(self):
        return " ".join(self.middle_list) or ""

    @property
    def last(self):
        return " ".join(self.last_list) or ""

    @property
    def suffix(self):
        return ", ".join(self.suffix_list) or ""

    @property
    def nickname(self):
        return " ".join(self.nickname_list) or ""

    @property
    def unparsable(self):
        return len(self) == 0

    @property
    def full_name(self):
        """The string output of the Name instance."""
        return str(self)


def is_title(value):
    """Is in the :py:data:`~nominally.config.titles.TITLES` set."""
    return value in config.TITLES


def is_conjunction(piece):
    """Is in the conjuctions set and not :py:func:`is_an_initial()`."""
    return piece.lower() in config.CONJUNCTIONS and not is_an_initial(piece)


def is_prefix(piece):
    """
    Lowercase and no periods version of piece is in the
    :py:data:`~nominally.config.prefixes.PREFIXES` set.
    """
    return piece in config.PREFIXES


def is_roman_numeral(value):
    """
    Matches the ``roman_numeral`` regular expression in
    :py:data:`~nominally.config.regexes.REGEXES`.
    """
    return bool(config.RE_ROMAN_NUMERAL.match(value))


def is_suffix(piece):
    return piece in config.SUFFIXES and not is_an_initial(piece)


def are_suffixes(pieces):
    return all(is_suffix(x) for x in pieces)


def is_an_initial(value):
    return bool(config.RE_INITIAL.match(value))


def clean_input(s):
    # Note: nicknames have already been removed
    s = unidecode_expect_ascii(s).lower()
    s = re.sub('"|`', "'", s)  # convert all quotes/ticks to single quotes
    s = re.sub(";|:|,", ", ", s)  # convert : ; , to , with spacing
    s = re.sub(r"[-_/\\:]+", "-", s)  # convert _ / \ - : to single hyphen
    s = re.sub(r"[^-\sa-z0-9',]+", "", s)  # drop most all but - ' ,
    s = re.sub(r"\s+", " ", s)  # condense all whitespace to single space
    s = s.strip("- ")  # drop leading/trailing hyphens and spaces
    return s
