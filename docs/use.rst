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
       cleaned: {'havelock vetinari', 'dog-botherer'}
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


In the Console
-------------------

.. code-block::

    $ nominally "St John Nobbs, Cecil (Nobby) Wormsborough"
           raw: St John Nobbs, Cecil (Nobby) Wormsborough
       cleaned: {'nobby', 'st john nobbs, cecil wormsborough'}
        parsed: st john nobbs, cecil (nobby) wormsborough
          list: ['', 'cecil', 'wormsborough', 'st john nobbs', '', 'nobby']
         title:
         first: cecil
        middle: wormsborough
          last: st john nobbs
        suffix:
      nickname: nobby

Extended Examples
-------------------

See https://github.com/vaneseltine/nominally-examples/
for detailed examples of nominally usage.