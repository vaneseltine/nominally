.. toctree::
    :maxdepth: 2

.. _faq:

FAQ
=====================================


Input format
-------------------------------------

Nominally does one thing: take a name and parse it.
The name must arrive as a Unicode string.
If you are working with bytes as input,
you will first need to decode them.

For assistance in working with Unicode strings, see:
    - `Python 3 Documentation, "Unicode HOWTO" <https://docs.python.org/3/howto/unicode.html>`_
    - `Ned Batchelder, "Pragmatic Unicode" <https://nedbatchelder.com/text/unipain.html>`_
    - `Joel Spolsky, "The Absolute Minimum Every Software Developer Absolutely, Positively Must Know About Unicode and Character Sets (No Excuses!)" <https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/>`_

Nominally takes input one name at a time.

For ideas about how to use Nominally on a larger scale,
to work with entire lists, DataFrames, files, or databases,
see https://github.com/vaneseltine/nominally-examples/.

Name cleaning
-------------------------------------

No canonical names.

Strings are *aggressively* cleaned.
    -

For specifics, see

Name ordering
-------------------------------------

We only handle
`Western name order <https://en.wikipedia.org/wiki/Personal_name#Name_order>`_.
No effort is made to disentangle or rearrange names
based on their origins.

We do not preserve suffix or title ordering.
Treat these as sets.

Titles and suffixes
-------------------------------------

We handle few suffixes:
    - PhD
    - MD
    - Sr
    - Junior, Jr, II, 2nd, III, 3rd, IV, 4th

We handle very few titles:
    - Dr.
    - Mr.
    - Mrs.
    - Ms.

These are treated as unordered sets.


Library
-------------------------------------

The Name class creates immutable instances.
