.. toctree::
    :maxdepth: 2


.. _use:

Use
======

.. _installation:

Installation
---------------

Install in the normal way:

.. code-block::

    pip install nominally

Starting a new project
`by creating a virtual environment <https://docs.python.org/3/tutorial/venv.html>`_
first is highly recommended:

.. code-block:: shell

    # Create a virtual environment
    python -m venv .venv

    # Activate with one of the following shell-specific scripts.
    # Note that Python for Windows creates ./Scripts/ rather than ./bin/
    # . .venv/bin/activate.fish         # fish
    # source ./.venv/bin/activate       # bash
    # source ./.venv/bin/activate.csh   # csh
    # .\.venv\Scripts\Activate.ps1      # PowerShell
    # .venv\Scripts\Activate.bat        # cmd

    # Install
    pip install nominally


Nominally requires Python 3.6 or higher and
has one external dependency
(`unidecode <https://pypi.org/project/Unidecode/>`_).

.. _examples:

Via Import
---------------

The :py:func:`nominally.api.parse_name` function
returns the five core fields:

.. runblock:: pycon

    >>> import nominally
    >>> from pprint import pprint
    >>> parsed = nominally.parse_name('Samuel "Young Sam" Vimes II')
    >>> pprint(parsed)

And :py:func:`nominally.api.report` returns the more detailed dict
as used in the command line interface:

.. runblock:: pycon

    >>> import nominally
    >>> nominally.report("Havelock 'Dog-Botherer' Vetinari")

Additional features are exposed via
the :py:class:`nominally.parser.Name` class:

.. runblock:: pycon

    >>> from nominally import Name
    >>> from pprint import pprint
    >>> n = Name('Delphine Angua von Uberwald')
    >>> pprint(n.report())
    >>> n.raw
    >>> n.cleaned
    >>> n.first
    >>> n['first']
    >>> n.get('first')
    >>> pprint(dict(n))


In the Console
-------------------

.. runblock:: console

    $ nominally "St John Nobbs, Cecil (Nobby) Wormsborough"

Extended Examples
-------------------

See https://github.com/vaneseltine/nominally-examples/
for detailed examples of nominally usage.
