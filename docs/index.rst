.. nominally documentation master file

*nominally*: *a* *maximum-strength* *name* *parser* *for* *record* *linkage*


.. toctree::
   :maxdepth: 2
   :caption: Contents:


What Nominally Does
===================

Nominally simplifies and parses a personal name written in
`Western name order <https://en.wikipedia.org/wiki/Personal_name#Name_order>`_.
A name is parsed into five core fields:

1. Title
2. First
3. Middle
4. Last
5. Suffix

These should be fairly self-explanatory; read on for examples.

A command line tool is provided for convenience,
but the expected use case involves parsing
a list (or an np.Series or a pd.DataFrame) of names.

What Nominally Is Not Intended to Do
=====================================

- Present canonical names; strings are *aggressively* cleaned.
- Preserve suffix or title ordering (treat these as sets).
- Handle particularly many suffixes (PhD, MD, generational up to IV).
- Handle particularly many titles (Dr. Mr. Mrs., and Ms. are about it).
- Handle any non-Western name ordering.
- Receive input other than Python 3 strings in UTF-8.
- Support mutability of name instances.
- Support mononyms.


Installation
============

Install via ``pip install nominally``.
Nominally requires Python 3.6 or higher and
has one external dependency
(`unidecode <https://pypi.org/project/Unidecode/>`_).


Example at the Console
=========================

.. code-block::

    > nominally "St John Nobbs, Cecil Nobbs Wormsborough"

           raw: St John Nobbs, Cecil Nobbs Wormsborough
       cleaned: {'st john nobbs, cecil nobbs wormsborough'}
        parsed: st john nobbs, cecil nobbs wormsborough
          list: ['', 'cecil', 'nobbs wormsborough', 'st john nobbs', '', '']
         title:
         first: cecil
        middle: nobbs wormsborough
          last: st john nobbs
        suffix:
      nickname:

Example via Import
=========================

The :py:func:`nominally.api.parse_name` function returns the five core fields:

.. code-block:: python

    >>> import nominally
    >>> nominally.parse_name('Samuel "Young Sam" Vimes II')
    {
        'title': '',
        'first': 'samuel',
        'middle': '',
        'last': 'vimes',
        'suffix': 'ii',
        'nickname': 'young sam'
    }

And :py:func:`nominally.api.report` returns the more detailed dict
as used in the command line interface:

    >>> import nominally
    >>> nominally.report("Havelock 'Dog-botherer' Vetinari")
        raw: Havelock 'Dog-botherer' Vetinari
    cleaned: {'dog-botherer', 'havelock vetinari'}
        parsed: vetinari, havelock (dog-botherer)
        list: ['', 'havelock', '', 'vetinari', '', 'dog-botherer']
        title:
        first: havelock
        middle:
        last: vetinari
        suffix:
    nickname: dog-botherer

Additional features are exposed via
the :py:class:`nominally.parser.Name` class:

.. code-block:: python

    >>> from nominally import Name
    >>> n = Name('Delphine Angua von Überwald')
    >>> n.report()
    {
        'raw': 'Delphine Angua von Überwald',
        'cleaned': {'delphine angua von uberwald'},
        'parsed': 'von uberwald, delphine angua',
        'list': ['', 'delphine', 'angua', 'von uberwald', '', ''],
        'title': '',
        'first': 'delphine',
        'middle': 'angua',
        'last': 'von uberwald',
        'suffix': '', 'nickname': ''
    }
    >>> n.raw
    'Delphine Angua von Überwald'
    >>> n.cleaned
    {'delphine angua von uberwald'}
    >>> n.first
    'delphine'
    >>> n['first']
    'delphine'
    >>> n.get('first')
    'delphine'
    >>> dict(n)
    {
      'title': '',
      'first': 'delphine',
      'middle': 'angua',
      'last': 'von uberwald',
      'suffix': '',
      'nickname': ''
    }

More Examples
==================

See https://github.com/vaneseltine/nominally-examples/
for detailed examples of nominally usage.

How the Sausage is Made
============================

.. automodule:: nominally.api
   :members:
   :undoc-members:

.. automodule:: nominally.parser
   :members:
   :undoc-members:

Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
