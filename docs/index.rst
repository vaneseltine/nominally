.. nominally documentation master file

Introduction
================================

*Nominally* simplifies and parses a personal name written in
`Western name order <https://en.wikipedia.org/wiki/Personal_name#Name_order>`_
into five core fields: title, first, middle, last, and suffix.

Typically, *nominally* is used to parse entire lists or
`pd.Series <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html>`_
of names en masse. This package includes a command line tool
to parse a single name for convenient one-off testing and examples.


Design Goals
--------------------------

*Nominally* is designed to assist at the front end of record linkage, during
data preprocessing.

Varying quality and practices across institutions and datasets introduce noise
into data and cause misrepresentation. This increases the challenges of
deduplicating rows within data and and linking names across multiple datasets.
We observe this by-no-means-exhaustive list:

    - First and middle names split arbitrarily.
    - Misplaced prefixes of last names (e.g., "van" and "de la").
    - Records with multiple last names partitioned into middle name fields.
    - Titles and suffixes various recorded in fields and/or with separators.
    - Inconsistent capture of accents and other non-ASCII characters.
    - Single name fields concatenating name parts arbitrarily.


In attempting to match someone named Ramsay Jackson Canning across data,
one may uncover "R.J. CANNING," "Canning, Ramsay J.," "Ramsay "R.J." Jackson
Canning," "Dr. Ramsay Jackson Canning, M.D.," "canning, jr., dr. ramsay"—and
so on.

*Nominally* can't fix all these data problems (sorry).

But it can help by **consistently extracting the most useful features of
personal names** under the highly restrictive case of a single string name
field. *Nominally* :ref:`aggressively cleans <cleaning>`, scrapes titles,
nicknames, and suffixes, and parses apart first, middle, and last names.

The process of converting input to output in *nominally* is
`idempotent <https://en.wikipedia.org/wiki/Idempotence>`_.
Parsing and reparsing any name will not change the outcome, even when
its output has been condensed to a single-field string representation.
In other words, for all *x*:

.. math::

   Name(Name(x)) = Name(x)


Contents
----------------------------

.. toctree::
    :maxdepth: 2

    self
    use
    faq
    sausage
    about


Indices and tables
----------------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
