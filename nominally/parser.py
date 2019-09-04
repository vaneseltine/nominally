import logging
import re

from unidecode import unidecode_expect_ascii

from nominally import config

LOGS_ON = True

logger = logging.getLogger()
if LOGS_ON:
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
else:
    logger.addHandler(logging.NullHandler())


def parse_name(s):
    return Name(s).as_dict()


class Name:
    """
    Parse a person's name into individual components.

    Instantiation assigns to ``full_name``, and assignment to
    :py:attr:`full_name` triggers :py:func:`parse_full_name`. After parsing the
    name, these instance attributes are available.

    **Name Instance Attributes**

    * :py:attr:`title`
    * :py:attr:`first`
    * :py:attr:`middle`
    * :py:attr:`last`
    * :py:attr:`suffix`
    * :py:attr:`nickname`

    :param str full_name: The name string to be parsed.
    """

    _count = 0
    _members = ["title", "first", "middle", "last", "suffix", "nickname"]

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

    def __iter__(self):
        return self

    def __len__(self):
        return len([v for k, v in self.as_dict().items() if v])

    def __eq__(self, other):
        if self.unparsable:
            return False
        return str(self).lower() == str(other).lower()

    def __getitem__(self, key):
        return getattr(self, key)

    def __next__(self):
        if self._count >= len(self._members):
            self._count = 0
            raise StopIteration
        else:
            c = self._count
            self._count = c + 1
            return getattr(self, self._members[c]) or next(self)

    def __str__(self):
        s = " ".join(
            x
            for x in [self.title, self.first, self.middle, self.last, self.suffix]
            if x
        )
        if self.nickname:
            s += f" ({self.nickname})"
        return collapse_whitespace(s).strip(", ")

    def __repr__(self):
        if self.unparsable:
            return f"{self.__class__.__name__}(Unparsable)"
        return f"{self.__class__.__name__}({self.as_dict()})"

    def as_dict(self, include_empty=True):
        """Return the parsed name as a dictionary of its attributes."""
        return {m: getattr(self, m) for m in self._members}

    def pre_process(self):
        """
        This method happens at the beginning of the :py:func:`parse_full_name`
        before any other processing of the string aside from unicode
        normalization, so it's a good place to do any custom handling in a
        subclass. Runs :py:func:`parse_nicknames` .
        """
        self.parse_nicknames()
        self.thoroughly_clean()

    def post_process(self):
        """
        This happens at the end of the :py:func:`parse_full_name` after
        all other processing has taken place.
        """
        self.make_last_name_if_title_and_one()

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
        self._full_name = clean_name(self._full_name)

    def make_last_name_if_title_and_one(self):
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
        parts = [x.strip() for x in self._full_name.split(",")]

        logger.debug("full_name: %s", self._full_name)
        logger.debug("parts: %s", parts)

        if len(parts) == 1:

            # ~ no commas, title first middle middle middle last suffix
            # ~           part[0]

            pieces = self.parse_pieces(parts, additional_parts_count=0)
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
        else:
            # if all the end parts are suffixes and there is more than one piece
            # in the first part. (Suffixes will never appear after last names
            # only, and allows potential first names to be in suffixes, e.g.
            # "Johnson, Bart"
            if are_suffixes(parts[1].split(" ")) and len(parts[0].split(" ")) > 1:

                # suffix comma:
                # * title first middle last [suffix], suffix [suffix] [, suffix]
                # *               parts[0],          parts[1:...]

                self.suffix_list += parts[1:]
                pieces = self.parse_pieces(
                    parts[0].split(" "), additional_parts_count=0
                )
                logger.debug(f"pieces: {pieces}")
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
            else:

                # lastname comma:
                # * last [suffix], title first middles[,] suffix [,suffix]
                # *     parts[0],      parts[1],              parts[2:...]
                pieces = self.parse_pieces(
                    parts[1].split(" "), additional_parts_count=1
                )

                logger.debug(f"pieces: {pieces}")

                # lastname part may have suffixes in it
                lastname_pieces = self.parse_pieces(
                    parts[0].split(" "), additional_parts_count=1
                )
                for piece in lastname_pieces:
                    # the first one is always a last name, even if it looks like
                    # a suffix
                    if is_suffix(piece) and len(self.last_list) > 0:
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

        if self.unparsable:
            logger.info('Unparsable: "%s" ', self.original)

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
        output = []
        # for part in self.properly_list_pieces(parts):
        for part in parts:
            output += [x.strip(" ,") for x in part.split(" ")]

        logger.debug(f"Incoming pieces: {output}")
        pieces = self.join_on_conjunctions(output, additional_parts_count)
        pieces = self.join_prefixes(pieces, original=output)
        logger.debug(f"Outgoing pieces: {pieces}")
        return pieces

    def join_on_conjunctions(self, pieces, additional_parts_count=0):
        """
        Join conjunctions to surrounding pieces. Title- and prefix-aware. e.g.:

            ['Mr.', 'and'. 'Mrs.', 'John', 'Doe'] ==>
                            ['Mr. and Mrs.', 'John', 'Doe']

            ['The', 'Secretary', 'of', 'State', 'Hillary', 'Clinton'] ==>
                            ['The Secretary of State', 'Hillary', 'Clinton']

        When joining titles, saves newly formed piece to the instance's titles
        constant so they will be parsed correctly later. E.g. after parsing the
        example names above, 'The Secretary of State' and 'Mr. and Mrs.' would
        be present in the titles constant set.

        :param list pieces: name pieces strings after split on spaces
        :param int additional_parts_count:
        :return: new list with piece next to conjunctions merged into one piece
        with spaces in it.
        :rtype: list

        """
        if len(pieces) == 1:
            return pieces
        original = pieces.copy()

        length = len(pieces) + additional_parts_count
        logger.debug(f"length {length} additional_parts_count {additional_parts_count}")
        # don't join on conjunctions if there's only 2 parts
        if length < 3:
            return original

        conj_index = [i for i, piece in enumerate(pieces) if is_conjunction(piece)]
        logger.debug(f"conj_index: {conj_index}")

        for i in conj_index:
            new_piece = " ".join(pieces[i - 1 : i + 2])
            pieces[i - 1] = new_piece
            pieces.pop(i)
            pieces.pop(i)

        if len(pieces) == 1:
            logger.debug("pieces: %s", pieces)
            logger.debug("Not expecting to arrive at only one piece; throwing back")
            return original

        return pieces

    def join_prefixes(self, pieces, original):
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
            return original
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


def collapse_whitespace(s):
    # collapse multiple spaces into single space
    return config.RE_SPACES.sub(" ", s.strip())


def is_title(value):
    """Is in the :py:data:`~nominally.config.titles.TITLES` set."""
    return lc(value) in config.TITLES


def is_conjunction(piece):
    """Is in the conjuctions set and not :py:func:`is_an_initial()`."""
    return piece.lower() in config.CONJUNCTIONS and not is_an_initial(piece)


def is_prefix(piece):
    """
    Lowercase and no periods version of piece is in the
    :py:data:`~nominally.config.prefixes.PREFIXES` set.
    """
    return lc(piece) in config.PREFIXES


def is_roman_numeral(value):
    """
    Matches the ``roman_numeral`` regular expression in
    :py:data:`~nominally.config.regexes.REGEXES`.
    """
    return bool(config.RE_ROMAN_NUMERAL.match(value))


def is_suffix(piece):
    """
    Is in the suffixes set and not :py:func:`is_an_initial()`.

    Some suffixes may be acronyms (M.B.A) while some are not (Jr.),
    so we remove the periods from `piece` when testing against
    `C.suffix_acronyms`.
    """
    # suffixes may have periods inside them like "M.D."
    return (
        (lc(piece).replace(".", "") in config.SUFFIX_ACRONYMS)
        or (lc(piece) in config.SUFFIX_NOT_ACRONYMS)
    ) and not is_an_initial(piece)


def are_suffixes(pieces):
    return all(is_suffix(x) for x in pieces)


def is_an_initial(value):
    return bool(config.RE_INITIAL.match(value))


def lc(value):
    """Lower case and remove any periods to normalize for comparison."""
    if not value:
        return ""
    return value.lower().strip(".")


def clean_name(s):
    s = unidecode_expect_ascii(s).lower()
    # s = re.sub(r"`|'|\"", "'", s)
    s = s.replace("`", "'")
    s = s.replace('"', "'")
    s = re.sub(r"[-_/\\]+", "-", s)
    s = re.sub(r"[^ \-a-z'\"(),]+", "", s)
    s = re.sub(r"\s+", " ", s)  # condense spaces
    s = s.strip("- ")
    return s
