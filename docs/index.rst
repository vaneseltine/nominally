.. nominally documentation master file

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

If you're already looking for a way to parse personal names,
these should be fairly self-explanatory, but do see :ref:`examples`.

A command line tool is provided for convenience,
but the expected use case involves parsing
a list or
`pd.Series <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html>`_
of names.

Record Linkage
--------------------------

When deduplicating names in a database or matching people across
multiple datasets, varying practices and quality across datasets
introduce noise and misrepresentation. For example, titles and suffixes
are often inconsistently recorded, or not recorded at all. Prefixes
of last names (e.g., "van" and "de la") are misplaced among middle names.
First and middle name splits may be arbitrary. More than one last name
may be partitioned into middle name. Names might or might not use accents
and other characters outside the standard ASCII table.

Nominally is designed for the front end of data preprocessing for
record linkage, aggressively cleaning and extracting features
of personal names.

Nominally's name parsing is
`idempotent <https://en.wikipedia.org/wiki/Idempotence>`_.
Parsing and reparsing any name will not change the outcome, even when
condensing Nominally's output to a single-field string representation.

Other great Python packages targeting record linkage include:
    - https://github.com/J535D165/recordlinkage
    - https://github.com/dedupeio/dedupe
    - https://github.com/usc-isi-i2/rltk

Contents
=========

.. toctree::
    :maxdepth: 2

    basics
    faq
    sausage

Indices and tables
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
