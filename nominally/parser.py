import sys
from itertools import groupby
from operator import itemgetter

from nominally import util
from nominally.config import CONSTANTS, Constants
from nominally.util import binary_type, lc, log, text_types, u


def group_contiguous_integers(data):
    """
    return list of tuples containing first and last index
    position of contiguous numbers in a series
    """
    ranges = []
    for key, group in groupby(enumerate(data), lambda i: i[0] - i[1]):
        group = list(map(itemgetter(1), group))
        if len(group) > 1:
            ranges.append((group[0], group[-1]))
    return ranges


class HumanName(object):
    """
    Parse a person's name into individual components.

    Instantiation assigns to ``full_name``, and assignment to
    :py:attr:`full_name` triggers :py:func:`parse_full_name`. After parsing the
    name, these instance attributes are available.

    **HumanName Instance Attributes**

    * :py:attr:`title`
    * :py:attr:`first`
    * :py:attr:`middle`
    * :py:attr:`last`
    * :py:attr:`suffix`
    * :py:attr:`nickname`
    * :py:attr:`surnames`

    :param str full_name: The name string to be parsed.
    :param str string_format: python string formatting
    """

    """
    A reference to the configuration for this instance, which may or may not be
    a reference to the shared, module-wide instance at
    :py:mod:`~nominally.config.CONSTANTS`. See `Customizing the Parser
    <customize.html>`_.
    """

    _count = 0
    _members = ["title", "first", "middle", "last", "suffix", "nickname"]

    def __init__(self, full_name="", constants=CONSTANTS, string_format=None):
        self.original = ""
        self._full_name = ""
        self.unparsable = True

        self.string_format = string_format or CONSTANTS.string_format
        # full_name setter triggers the parse
        self.full_name = full_name

    def __iter__(self):
        return self

    def __len__(self):
        l = 0
        for x in self:
            l += 1
        return l

    def __eq__(self, other):
        """
        HumanName instances are equal to other objects whose
        lower case unicode representation is the same.
        """
        return str(self).lower() == str(other).lower()

    def __ne__(self, other):
        return not (u(self)).lower() == (u(other)).lower()

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [getattr(self, x) for x in self._members[key]]
        else:
            return getattr(self, key)

    def __setitem__(self, key, value):
        if key in self._members:
            self._set_list(key, value)
        else:
            raise KeyError("Not a valid HumanName attribute", key)

    def next(self):
        return self.__next__()

    def __next__(self):
        if self._count >= len(self._members):
            self._count = 0
            raise StopIteration
        else:
            c = self._count
            self._count = c + 1
            return getattr(self, self._members[c]) or next(self)

    def __str__(self):
        if self.string_format:
            # string_format = "{title} {first} {middle} {last} {suffix} ({nickname})"
            _s = self.string_format.format(**self.as_dict())
            # remove trailing punctuation from missing nicknames
            _s = _s.replace(" ()", "")
            _s = _s.replace(" ''", "")
            _s = _s.replace(' ""', "")
            return self.collapse_whitespace(_s).strip(", ")
        return " ".join(self)

    def __repr__(self):
        if self.unparsable:
            _string = "<%(class)s : [ Unparsable ] >" % {
                "class": self.__class__.__name__
            }
        else:
            _string = (
                "<%(class)s : [\n\ttitle: '%(title)s' \n\tfirst: '%(first)s' \n\tmiddle: '%(middle)s' \n\tlast: '%(last)s' \n\tsuffix: '%(suffix)s'\n\tnickname: '%(nickname)s'\n]>"
                % {
                    "class": self.__class__.__name__,
                    "title": self.title or "",
                    "first": self.first or "",
                    "middle": self.middle or "",
                    "last": self.last or "",
                    "suffix": self.suffix or "",
                    "nickname": self.nickname or "",
                }
            )
        return _string

    def as_dict(self, include_empty=True):
        """
        Return the parsed name as a dictionary of its attributes.

        :param bool include_empty: Include keys in the dictionary for empty name attributes.
        :rtype: dict

        .. doctest::

            >>> name = HumanName("Bob Dole")
            >>> name.as_dict()
            {'last': 'Dole', 'suffix': '', 'title': '', 'middle': '', 'nickname': '', 'first': 'Bob'}
            >>> name.as_dict(False)
            {'last': 'Dole', 'first': 'Bob'}

        """
        d = {}
        for m in self._members:
            if include_empty:
                d[m] = getattr(self, m)
            else:
                val = getattr(self, m)
                if val:
                    d[m] = val
        return d

    ### attributes

    @property
    def title(self):
        """
        The person's titles. Any string of consecutive pieces in
        :py:mod:`~nominally.config.titles` or
        :py:mod:`~nominally.config.conjunctions`
        at the beginning of :py:attr:`full_name`.
        """
        return " ".join(self.title_list) or ""

    @property
    def first(self):
        """
        The person's first name. The first name piece after any known
        :py:attr:`title` pieces parsed from :py:attr:`full_name`.
        """
        return " ".join(self.first_list) or ""

    @property
    def middle(self):
        """
        The person's middle names. All name pieces after the first name and
        before the last name parsed from :py:attr:`full_name`.
        """
        return " ".join(self.middle_list) or ""

    @property
    def last(self):
        """
        The person's last name. The last name piece parsed from
        :py:attr:`full_name`.
        """
        return " ".join(self.last_list) or ""

    @property
    def suffix(self):
        """
        The persons's suffixes. Pieces at the end of the name that are found in
        :py:mod:`~nominally.config.suffixes`, or pieces that are at the end
        of comma separated formats, e.g.
        "Lastname, Title Firstname Middle[,] Suffix [, Suffix]" parsed
        from :py:attr:`full_name`.
        """
        return ", ".join(self.suffix_list) or ""

    @property
    def nickname(self):
        """
        The person's nicknames. Any text found inside of quotes (``""``) or
        parenthesis (``()``)
        """
        return " ".join(self.nickname_list) or ""

    @property
    def surnames_list(self):
        """
        List of middle names followed by last name.
        """
        return self.middle_list + self.last_list

    @property
    def surnames(self):
        """
        A string of all middle names followed by the last name.
        """
        return " ".join(self.surnames_list) or ""

    ### setter methods

    def _set_list(self, attr, value):
        if isinstance(value, list):
            val = value
        elif isinstance(value, text_types):
            val = [value]
        elif value is None:
            val = []
        else:
            raise TypeError(
                "Can only assign strings, lists or None to name attributes."
                " Got {0}".format(type(value))
            )
        setattr(self, attr + "_list", self.parse_pieces(val))

    @title.setter
    def title(self, value):
        self._set_list("title", value)

    @first.setter
    def first(self, value):
        self._set_list("first", value)

    @middle.setter
    def middle(self, value):
        self._set_list("middle", value)

    @last.setter
    def last(self, value):
        self._set_list("last", value)

    @suffix.setter
    def suffix(self, value):
        self._set_list("suffix", value)

    @nickname.setter
    def nickname(self, value):
        self._set_list("nickname", value)

    ### Parse helpers

    def is_title(self, value):
        """Is in the :py:data:`~nominally.config.titles.TITLES` set."""
        return lc(value) in CONSTANTS.titles

    def is_conjunction(self, piece):
        """Is in the conjuctions set and not :py:func:`is_an_initial()`."""
        return piece.lower() in CONSTANTS.conjunctions and not self.is_an_initial(piece)

    def is_prefix(self, piece):
        """
        Lowercase and no periods version of piece is in the
        :py:data:`~nominally.config.prefixes.PREFIXES` set.
        """
        return lc(piece) in CONSTANTS.prefixes

    def is_roman_numeral(self, value):
        """
        Matches the ``roman_numeral`` regular expression in
        :py:data:`~nominally.config.regexes.REGEXES`.
        """
        return False
        return bool(CONSTANTS.regexes.roman_numeral.match(value))

    def is_suffix(self, piece):
        """
        Is in the suffixes set and not :py:func:`is_an_initial()`.

        Some suffixes may be acronyms (M.B.A) while some are not (Jr.),
        so we remove the periods from `piece` when testing against
        `C.suffix_acronyms`.
        """
        # suffixes may have periods inside them like "M.D."
        return (
            (lc(piece).replace(".", "") in CONSTANTS.suffix_acronyms)
            or (lc(piece) in CONSTANTS.suffix_not_acronyms)
        ) and not self.is_an_initial(piece)

    def are_suffixes(self, pieces):
        """Return True if all pieces are suffixes."""
        for piece in pieces:
            if not self.is_suffix(piece):
                return False
        return True

    def is_rootname(self, piece):
        """
        Is not a known title, suffix or prefix. Just first, middle, last names.
        """
        return lc(
            piece
        ) not in CONSTANTS.suffixes_prefixes_titles and not self.is_an_initial(piece)

    def is_an_initial(self, value):
        """
        Words with a single period at the end, or a single uppercase letter.

        Matches the ``initial`` regular expression in
        :py:data:`~nominally.config.regexes.REGEXES`.
        """
        return bool(CONSTANTS.regexes.initial.match(value))

    ### full_name parser

    @property
    def full_name(self):
        """The string output of the HumanName instance."""
        return self.__str__()

    @full_name.setter
    def full_name(self, value):
        self.original = value
        self._full_name = value.lower()
        self.parse_full_name()

    def collapse_whitespace(self, string):
        # collapse multiple spaces into single space
        string = CONSTANTS.regexes.spaces.sub(" ", string.strip())
        if string.endswith(","):
            string = string[:-1]
        return string

    def pre_process(self):
        """

        This method happens at the beginning of the :py:func:`parse_full_name`
        before any other processing of the string aside from unicode
        normalization, so it's a good place to do any custom handling in a
        subclass. Runs :py:func:`parse_nicknames` .

        """
        self.parse_nicknames()
        # self.thoroughly_clean()

    def post_process(self):
        """
        This happens at the end of the :py:func:`parse_full_name` after
        all other processing has taken place. Runs :py:func:`handle_firstnames`.
        """
        self.handle_firstnames()

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

        re_quoted_word = CONSTANTS.regexes.quoted_word
        re_double_quotes = CONSTANTS.regexes.double_quotes
        re_parenthesis = CONSTANTS.regexes.parenthesis

        for _re in (re_quoted_word, re_double_quotes, re_parenthesis):
            if _re.search(self._full_name):
                self.nickname_list += [x for x in _re.findall(self._full_name)]
                self._full_name = _re.sub("", self._full_name)

    def thoroughly_clean(self):
        self._full_name = util.clean(self._full_name)

    def handle_firstnames(self):
        """
        If there are only two parts and one is a title, assume it's a last name
        instead of a first name. e.g. Mr. Johnson. Unless it's a special title
        like "Sir", then when it's followed by a single name that name is always
        a first name.
        """
        if (
            self.title
            and len(self) == 2
            and not lc(self.title) in CONSTANTS.first_name_titles
        ):
            self.last, self.first = self.first, self.last

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

        self.title_list = []
        self.first_list = []
        self.middle_list = []
        self.last_list = []
        self.suffix_list = []
        self.nickname_list = []
        self.unparsable = True

        self.pre_process()

        self._full_name = self.collapse_whitespace(self._full_name)

        # break up full_name by commas
        parts = [x.strip() for x in self._full_name.split(",")]

        log.debug("full_name: %s", self._full_name)
        log.debug("parts: %s", parts)

        if len(parts) == 1:

            # no commas, title first middle middle middle last suffix
            #            part[0]

            pieces = self.parse_pieces(parts)
            p_len = len(pieces)
            for i, piece in enumerate(pieces):
                try:
                    nxt = pieces[i + 1]
                except IndexError:
                    nxt = None

                # title must have a next piece, unless it's just a title
                if self.is_title(piece) and (nxt or p_len == 1) and not self.first:
                    self.title_list.append(piece)
                    continue
                if not self.first:
                    if p_len == 1 and self.nickname:
                        self.last_list.append(piece)
                        continue
                    self.first_list.append(piece)
                    continue
                if self.are_suffixes(pieces[i + 1 :]) or (
                    # if the next piece is the last piece and a roman
                    # numeral but this piece is not an initial
                    self.is_roman_numeral(nxt)
                    and i == p_len - 2
                    and not self.is_an_initial(piece)
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
            if self.are_suffixes(parts[1].split(" ")) and len(parts[0].split(" ")) > 1:

                # suffix comma:
                # title first middle last [suffix], suffix [suffix] [, suffix]
                #               parts[0],          parts[1:...]

                self.suffix_list += parts[1:]
                pieces = self.parse_pieces(parts[0].split(" "))
                log.debug("pieces: %s", u(pieces))
                for i, piece in enumerate(pieces):
                    try:
                        nxt = pieces[i + 1]
                    except IndexError:
                        nxt = None

                    if (
                        self.is_title(piece)
                        and (nxt or len(pieces) == 1)
                        and not self.first
                    ):
                        self.title_list.append(piece)
                        continue
                    if not self.first:
                        self.first_list.append(piece)
                        continue
                    if self.are_suffixes(pieces[i + 1 :]):
                        self.last_list.append(piece)
                        self.suffix_list = pieces[i + 1 :] + self.suffix_list
                        break
                    if not nxt:
                        self.last_list.append(piece)
                        continue
                    self.middle_list.append(piece)
            else:

                # lastname comma:
                # last [suffix], title first middles[,] suffix [,suffix]
                #      parts[0],      parts[1],              parts[2:...]
                pieces = self.parse_pieces(parts[1].split(" "), 1)

                log.debug("pieces: %s", u(pieces))

                # lastname part may have suffixes in it
                lastname_pieces = self.parse_pieces(parts[0].split(" "), 1)
                for piece in lastname_pieces:
                    # the first one is always a last name, even if it looks like
                    # a suffix
                    if self.is_suffix(piece) and len(self.last_list) > 0:
                        self.suffix_list.append(piece)
                    else:
                        self.last_list.append(piece)

                for i, piece in enumerate(pieces):
                    try:
                        nxt = pieces[i + 1]
                    except IndexError:
                        nxt = None

                    if (
                        self.is_title(piece)
                        and (nxt or len(pieces) == 1)
                        and not self.first
                    ):
                        self.title_list.append(piece)
                        continue
                    if not self.first:
                        self.first_list.append(piece)
                        continue
                    if self.is_suffix(piece):
                        self.suffix_list.append(piece)
                        continue
                    self.middle_list.append(piece)
                try:
                    if parts[2]:
                        self.suffix_list += parts[2:]
                except IndexError:
                    pass

        if len(self) < 0:
            log.info('Unparsable: "%s" ', self.original)
        else:
            self.unparsable = False
        self.post_process()

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
        for part in parts:
            if not isinstance(part, text_types):
                raise TypeError(
                    "Name parts must be strings. " "Got {0}".format(type(part))
                )
            output += [x.strip(" ,") for x in part.split(" ")]

        # If part contains periods, check if it's multiple titles or suffixes
        # together without spaces if so, add the new part with periods to the
        # constants so they get parsed correctly later
        for part in output:
            # if this part has a period not at the beginning or end
            if CONSTANTS.regexes.period_not_at_end.match(part):
                # split on periods, any of the split pieces titles or suffixes?
                # ("Lt.Gov.")
                period_chunks = part.split(".")
                titles = list(filter(self.is_title, period_chunks))
                suffixes = list(filter(self.is_suffix, period_chunks))

                # add the part to the constant so it will be found
                if len(list(titles)):
                    CONSTANTS.titles.add(part)
                    continue
                if len(list(suffixes)):
                    CONSTANTS.suffix_not_acronyms.add(part)
                    continue

        pieces = self.join_on_conjunctions(output, additional_parts_count)
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
        length = len(pieces) + additional_parts_count
        # don't join on conjunctions if there's only 2 parts
        if length < 3:
            return pieces

        rootname_pieces = [p for p in pieces if self.is_rootname(p)]
        total_length = len(rootname_pieces) + additional_parts_count

        # find all the conjunctions, join any conjunctions that are next to each
        # other, then join those newly joined conjunctions and any single
        # conjunctions to the piece before and after it
        conj_index = [i for i, piece in enumerate(pieces) if self.is_conjunction(piece)]

        contiguous_conj_i = []
        for i, val in enumerate(conj_index):
            try:
                if conj_index[i + 1] == val + 1:
                    contiguous_conj_i += [val]
            except IndexError:
                pass

        contiguous_conj_i = group_contiguous_integers(conj_index)

        delete_i = []
        if contiguous_conj_i:
            print(contiguous_conj_i)
        for i in contiguous_conj_i:
            if type(i) == tuple:
                new_piece = " ".join(pieces[i[0] : i[1] + 1])
                delete_i += list(range(i[0] + 1, i[1] + 1))
                pieces[i[0]] = new_piece
            else:
                new_piece = " ".join(pieces[i : i + 2])
                delete_i += [i + 1]
                pieces[i] = new_piece
            # add newly joined conjunctions to constants to be found later
            CONSTANTS.conjunctions.add(new_piece)

        for i in reversed(delete_i):
            # delete pieces in reverse order or the index changes on each delete
            del pieces[i]

        if len(pieces) == 1:
            # if there's only one piece left, nothing left to do
            return pieces

        # refresh conjunction index locations
        conj_index = [i for i, piece in enumerate(pieces) if self.is_conjunction(piece)]

        for i in conj_index:
            if len(pieces[i]) == 1 and total_length < 4:
                # if there are only 3 total parts (minus known titles, suffixes
                # and prefixes) and this conjunction is a single letter, prefer
                # treating it as an initial rather than a conjunction.
                # http://code.google.com/p/python-nominally/issues/detail?id=11
                continue

            if i is 0:
                new_piece = " ".join(pieces[i : i + 2])
                if self.is_title(pieces[i + 1]):
                    # when joining to a title, make new_piece a title too
                    CONSTANTS.titles.add(new_piece)
                pieces[i] = new_piece
                pieces.pop(i + 1)
                # subtract 1 from the index of all the remaining conjunctions
                for j, val in enumerate(conj_index):
                    if val > i:
                        conj_index[j] = val - 1

            else:
                new_piece = " ".join(pieces[i - 1 : i + 2])
                if self.is_title(pieces[i - 1]):
                    # when joining to a title, make new_piece a title too
                    CONSTANTS.titles.add(new_piece)
                pieces[i - 1] = new_piece
                pieces.pop(i)
                rm_count = 2
                try:
                    pieces.pop(i)
                except IndexError:
                    rm_count = 1

                # subtract the number of removed pieces from the index
                # of all the remaining conjunctions
                for j, val in enumerate(conj_index):
                    if val > i:
                        conj_index[j] = val - rm_count

        # join prefixes to following lastnames: ['de la Vega'], ['van Buren']
        prefixes = list(filter(self.is_prefix, pieces))
        if prefixes:
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
                    next_prefix = next(iter(filter(self.is_prefix, pieces[i + 1 :])))
                    j = pieces.index(next_prefix)
                    if j == i + 1:
                        # if there are two prefixes in sequence, join to the following piece
                        j += 1
                    new_piece = " ".join(pieces[i:j])
                    pieces = pieces[:i] + [new_piece] + pieces[j:]
                except StopIteration:
                    try:
                        # if there are no more prefixes, look for a suffix to stop at
                        stop_at = next(iter(filter(self.is_suffix, pieces[i + 1 :])))
                        j = pieces.index(stop_at)
                        new_piece = " ".join(pieces[i:j])
                        pieces = pieces[:i] + [new_piece] + pieces[j:]
                    except StopIteration:
                        # if there were no suffixes, nothing to stop at so join all
                        # remaining pieces
                        new_piece = " ".join(pieces[i:])
                        pieces = pieces[:i] + [new_piece]

        log.debug("pieces: %s", pieces)
        print(f"pieces: {pieces}")
        return pieces
