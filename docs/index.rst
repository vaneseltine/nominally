.. nominally documentation master file

Introduction
================================

**Nominally** simplifies and parses a personal name written in
`Western name order <https://en.wikipedia.org/wiki/Personal_name#Name_order>`_
into five core fields: title, first, middle, last, and suffix.

Typically, **nominally** is used to parse entire lists or
`pd.Series <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html>`_
of names en masse. This package includes a command line tool
to parse a single name for convenient one-off testing and examples.


Record Linkage
--------------------------

When deduplicating names in a database or matching people across multiple
datasets, varying practices and quality across datasets introduce
noise and misrepresentation. For example, titles and suffixes are often
inconsistently recorded, or not recorded at all. Prefixes of last names
(e.g., "van" and "de la") are misplaced among middle names. First and
middle name splits may be arbitrary. More than one last name may be
partitioned into middle name. Names might or might not use accents and
other characters outside the standard ASCII table.

**Nominally** is designed for the front end of data preprocessing for
record linkage, by :ref:`aggressively cleaning <cleaning>` and extracting
the most linkable features of personal names.

**Nominally** is
`idempotent <https://en.wikipedia.org/wiki/Idempotence>`_.
Parsing and reparsing any name will not change the outcome, even when
its output has been condensed to a single-field string representation.

See Also
~~~~~~~~~~~
More great Python packages in the record linkage community include:
    - `Python Record Linkage Toolkit <https://github.com/J535D165/recordlinkage>`_ by Jonathan de Bruin
    - `Dedupe Python Library <https://github.com/dedupeio/dedupe>`_ by Forest Gregg and Derek Eder
    - `RLTK: Record Linkage ToolKit <https://github.com/usc-isi-i2/rltk>`_ by the USC Center on Knowledge Graphs


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
