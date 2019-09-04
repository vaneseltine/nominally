# -*- coding: utf-8 -*-
"""
The :py:mod:`nominally.config` module manages the configuration of the
nominally.

A module-level instance of :py:class:`~nominally.config.Constants` is created
and used by default for all HumanName instances. You can adjust the entire module's
configuration by importing this instance and changing it.

::

    >>> from nominally.config import CONSTANTS
    >>> CONSTANTS.titles.remove('hon').add('chemistry','dean') # doctest: +ELLIPSIS
    SetManager(set([u'msgt', ..., u'adjutant']))

You can also adjust the configuration of individual instances by passing
``None`` as the second argument upon instantiation.

::

    >>> from nominally import HumanName
    >>> hn = HumanName("Dean Robert Johns", None)
    >>> hn.C.titles.add('dean') # doctest: +ELLIPSIS
    SetManager(set([u'msgt', ..., u'adjutant']))
    >>> hn.parse_full_name() # need to run this again after config changes

**Potential Gotcha**: If you do not pass ``None`` as the second argument,
``hn.C`` will be a reference to the module config, possibly yielding
unexpected results. See `Customizing the Parser <customize.html>`_.
"""
from collections import abc
import sys

from nominally.util import binary_type
from nominally.util import lc
from nominally.config.prefixes import PREFIXES
from nominally.config.conjunctions import CONJUNCTIONS
from nominally.config.suffixes import SUFFIX_ACRONYMS
from nominally.config.suffixes import SUFFIX_NOT_ACRONYMS
from nominally.config.titles import TITLES
from nominally.config.titles import FIRST_NAME_TITLES
from nominally.config.regexes import REGEXES


class SetManager(abc.Set):
    """
    Easily add and remove config variables per module or instance. Subclass of
    ``abc.Set``.

    Only special functionality beyond that provided by set() is
    to normalize constants for comparison (lower case, no periods)
    when they are add()ed and remove()d and allow passing multiple
    string arguments to the :py:func:`add()` and :py:func:`remove()` methods.

    """

    def __init__(self, elements):
        self.elements = set(elements)

    def __call__(self):
        return self.elements

    def __repr__(self):
        return "SetManager({})".format(self.elements)  # used for docs

    def __iter__(self):
        return iter(self.elements)

    def __contains__(self, value):
        return value in self.elements

    def __len__(self):
        return len(self.elements)

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.count >= len(self.elements):
            self.count = 0
            raise StopIteration
        else:
            c = self.count
            self.count = c + 1
            return getattr(self, self.elements[c]) or next(self)

    def add(self, *strings):
        """
        Add the lower case and no-period version of the string arguments to the set.
        Can pass a list of strings. Returns ``self`` for chaining.
        """
        for s in strings:
            self.elements.add(lc(s))
        return self

    def remove(self, *strings):
        """
        Remove the lower case and no-period version of the string arguments from the set.
        Returns ``self`` for chaining.
        """
        [self.elements.remove(lc(s)) for s in strings if lc(s) in self.elements]
        return self


class TupleManager(dict):
    """
    A dictionary with dot.notation access. Subclass of ``dict``. Makes the tuple constants
    more friendly.
    """

    def __getattr__(self, attr):
        return self.get(attr)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, state):
        self.__init__(state)

    def __reduce__(self):
        return (TupleManager, (), self.__getstate__())


class Constants(object):
    """
    An instance of this class hold all of the configuration constants for the parser.

    :param set prefixes:
        :py:attr:`prefixes` wrapped with :py:class:`SetManager`.
    :param set titles:
        :py:attr:`titles` wrapped with :py:class:`SetManager`.
    :param set first_name_titles:
        :py:attr:`~titles.FIRST_NAME_TITLES` wrapped with :py:class:`SetManager`.
    :param set suffix_acronyms:
        :py:attr:`~suffixes.SUFFIX_ACRONYMS`  wrapped with :py:class:`SetManager`.
    :param set suffix_not_acronyms:
        :py:attr:`~suffixes.SUFFIX_NOT_ACRONYMS`  wrapped with :py:class:`SetManager`.
    :param set conjunctions:
        :py:attr:`conjunctions`  wrapped with :py:class:`SetManager`.
    :type regexes: tuple or dict
    :param regexes:
        :py:attr:`regexes`  wrapped with :py:class:`TupleManager`.
    """

    string_format = "{title} {first} {middle} {last} {suffix} ({nickname})"
    """
    The default string format use for all new `HumanName` instances.
    """

    def __init__(
        self,
        prefixes=PREFIXES,
        suffix_acronyms=SUFFIX_ACRONYMS,
        suffix_not_acronyms=SUFFIX_NOT_ACRONYMS,
        titles=TITLES,
        first_name_titles=FIRST_NAME_TITLES,
        conjunctions=CONJUNCTIONS,
        regexes=REGEXES,
    ):
        self.prefixes = SetManager(prefixes)
        self.suffix_acronyms = SetManager(suffix_acronyms)
        self.suffix_not_acronyms = SetManager(suffix_not_acronyms)
        self.titles = SetManager(titles)
        self.first_name_titles = SetManager(first_name_titles)
        self.conjunctions = SetManager(conjunctions)
        self.regexes = TupleManager(regexes)
        self._pst = None

    @property
    def suffixes_prefixes_titles(self):
        if not self._pst:
            self._pst = (
                self.prefixes
                | self.suffix_acronyms
                | self.suffix_not_acronyms
                | self.titles
            )
        return self._pst

    def __repr__(self):
        return "<Constants() instance>"

    def __setstate__(self, state):
        self.__init__(state)

    def __getstate__(self):
        attrs = [x for x in dir(self) if not x.startswith("_")]
        return dict([(a, getattr(self, a)) for a in attrs])


#: A module-level instance of the :py:class:`Constants()` class.
#: Provides a common instance for the module to share
#: to easily adjust configuration for the entire module.
#: See `Customizing the Parser with Your Own Configuration <customize.html>`_.
CONSTANTS = Constants()
