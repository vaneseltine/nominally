<p align="center">
  <img src="https://raw.githubusercontent.com/vaneseltine/nominally/master/docs/_static/nominally_logo.png" alt="Nominally Logo" width=200 />
</p>

<h2 align="center">nominally: a maximum-strength name parser for record linkage</h2>

<p align="center">
  <a href="https://circleci.com/gh/vaneseltine/nominally">
    <img alt="Builds at CircleCI" src="https://img.shields.io/circleci/build/github/vaneseltine/nominally" />
  </a>
  <a href="https://codeclimate.com/github/vaneseltine/nominally">
    <img alt="Maintainability rated at Code Climate" src="https://img.shields.io/codeclimate/maintainability-percentage/vaneseltine/nominally">
  </a>
  <a href="https://nominally.readthedocs.io/en/latest/">
    <img alt="Documentation at Read the Docs" src="https://img.shields.io/readthedocs/nominally/latest?" />
  </a>
  <a href="https://snyk.io/test/github/vaneseltine/nominally/">
    <img alt="Vulnerabilities monitored by Snyk" src="https://snyk.io/test/github/vaneseltine/nominally/badge.svg" />
  </a>

</p>
<p align="center">
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img alt="License: AGPL 3.0+" src="https://img.shields.io/badge/license-AGPL-009999.svg" />
  </a>
  <a href="https://pypi.python.org/pypi/nominally">
    <img alt="Distributed via PyPI" src="https://img.shields.io/pypi/v/nominally?color=009999" />
  </a>
  <a href="https://joss.theoj.org/papers/d340ccbed7e8775b9fc3f4d5ee137fa0">
    <img src="https://joss.theoj.org/papers/d340ccbed7e8775b9fc3f4d5ee137fa0/status.svg">
  </a>
  <a href="https://github.com/vaneseltine/nominally">
    <img alt="Latest commit at GitHub" src="https://img.shields.io/github/last-commit/vaneseltine/nominally" />
  </a>
</p>

### 🔗 Names

_Nominally_ simplifies and parses a personal name written in
[Western name order](https://en.wikipedia.org/wiki/Personal_name#Name_order)
into six core fields: title, first, middle, last, suffix, and nickname.

Typically, _nominally_ is used to parse entire lists or
[pd.Series](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html)
of names en masse. This package includes a command line tool
to parse a single name for convenient one-off testing and examples.

Human names can be difficult to work with in data.
Varying quality and practices across institutions and datasets
introduce noise and cause misrepresentation,
increasing linkage and deduplication challenges.
Common errors and discrepancies include
(and this list is by no means exhaustive):

- Arbitrarily split first and middle names.
- Misplaced prefixes of last names such as "van" and "de la."
- Multiple last names partitioned into middle name fields.
- Titles and suffixes variously recorded in different fields, with or without separators.
- Inconsistent capture of accents, the ʻokina, and other non-ASCII characters.
- Single name fields arbitrarily concatenating name parts.

_Nominally_ produces fields intended for comparisons between or within datasets. As such, names come out formatted for data without regard to human syntactic preference: `de von ausfern, mr johann g` rather than
`Mr. Johann G. de von Ausfern`.

### 📜 Documentation

Full _nominally_ documentation is maintained on ReadTheDocs: https://nominally.readthedocs.io/en/latest/

### ⛏️ Installation

Releases of _nominally_ are [distributed on PyPI](https://pypi.org/project/nominally/), so the recommended approach is to install via pip:

```
$ python -m pip install -U nominally
```

### 📓 Getting Started

Call `parse_name()` to parse out the six core fields:

```
$ python -q
>>> from nominally import parse_name
>>> parse_name("Vimes, jr, Mr. Samuel 'Sam'")
{
    'title': 'mr',
    'first': 'samuel',
    'middle': '',
    'last': 'vimes',
    'suffix': 'jr',
    'nickname': 'sam'
}
```

Dive into the `Name` class to parse out a reformatted string...

```
>>> from nominally import Name
>>> n = Name("Vimes, jr, Mr. Samuel 'Sam'")
>>> n
Name({
  'title': 'mr',
  'first': 'samuel',
  'middle': '',
  'last': 'vimes',
  'suffix': 'jr',
  'nickname': 'sam'
})
>>> str(n)
'vimes, mr samuel (sam) jr'
```

...or use the dict...

```
>>> dict(n)
{
  'title': 'mr',
  'first': 'samuel',
  'middle': '',
  'last': 'vimes',
  'suffix': 'jr',
  'nickname': 'sam'
}
>>> list(n.values())
['mr', 'samuel', '', 'vimes', 'jr', 'sam']
```

...or retrieve a more elaborate set of attributes...

```
>>> n.report()
{
  'raw': "Vimes, jr, Mr. Samuel 'Sam'",
  'cleaned': {'jr', 'sam', 'vimes, mr samuel'},
  'parsed': 'vimes, mr samuel (sam) jr',
  'list': ['mr', 'samuel', '', 'vimes', 'jr', 'sam'],
  'title': 'mr',
  'first': 'samuel',
  'middle': '',
  'last': 'vimes',
  'suffix': 'jr',
  'nickname': 'sam'
}
```

...or capture individual attributes.

```
>>> n.first
'samuel'
>>> n['last']
'vimes'
>>> n.get('suffix')
'jr'
>>> n.raw
"Vimes, jr, Mr. Samuel 'Sam'"
```

### 🖥️ Command Line

For a quick report, invoke the `nominally` command line tool:

```
$ nominally "Vimes, jr, Mr. Samuel 'Sam'"
       raw: Vimes, jr, Mr. Samuel 'Sam'
   cleaned: {'jr', 'vimes, mr samuel', 'sam'}
    parsed: vimes, mr samuel (sam) jr
      list: ['mr', 'samuel', '', 'vimes', 'jr', 'sam']
     title: mr
     first: samuel
    middle:
      last: vimes
    suffix: jr
  nickname: sam
```

### 🔬 Worked Examples

Binder hosts live Jupyter notebooks walking through examples of _nominally_.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[![csv.ipynb on mybinder.org](https://img.shields.io/badge/launch_notebook-csv_parse-888.svg?style=for-the-badge&logo=jupyter&logoColor=fff&color=ff4785)](https://mybinder.org/v2/gh/vaneseltine/nominally-examples/master?filepath=notebooks%2Fcsv.ipynb)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[![pandas_simple.ipynb on mybinder.org](https://img.shields.io/badge/launch_notebook-pandas_apply-888.svg?style=for-the-badge&logo=jupyter&logoColor=fff&color=ff4785)](https://mybinder.org/v2/gh/vaneseltine/nominally-examples/master?filepath=notebooks%2Fpandas_simple.ipynb)

These notebooks and additional examples reside [in the Nominally Examples repository](https://github.com/vaneseltine/nominally-examples/).

### 👩‍💻 Community

Interested in helping to improve _nominally_? Please see [CONTRIBUTING.md](CONTRIBUTING.md).

[CONTRIBUTING.md](CONTRIBUTING.md) also includes directions to run tests, using a clone of the full repository.

Having problems with _nominally_? Need help or support? Feel free to [open an issue here on Github](https://github.com/vaneseltine/nominally/issues/new/choose), or contact me via email or Twitter ([see my profile for links](https://github.com/vaneseltine)).

### 🧙‍ Author

[![Matt VanEseltine](https://img.shields.io/badge/name-matt_vaneseltine-888.svg?style=for-the-badge&logo=linux&logoColor=fff&color=violet)](https://vaneseltine.github.io)

[![https://pypi.org/user/matvan/](https://img.shields.io/badge/pypi-matvan-888.svg?style=for-the-badge&logo=python&logoColor=fff&color=0073b7)](https://pypi.org/user/matvan/)

[![matvan@umich.edu](https://img.shields.io/badge/email-matvan@umich.edu-888.svg?style=for-the-badge&logo=gmail&logoColor=fff&color=00274c)](mailto:matvan@umich.edu)

[![https://github.com/vaneseltine](https://img.shields.io/badge/github-vaneseltine-888.svg?style=for-the-badge&logo=github&logoColor=fff&color=2b3137)](https://github.com/vaneseltine)

[![https://twitter.com/vaneseltine](https://img.shields.io/badge/twitter-@vaneseltine-blue.svg?style=for-the-badge&logo=twitter&logoColor=fff&color=1da1f2)](https://twitter.com/vaneseltine)

[![https://stackoverflow.com/users/7846185/matt-vaneseltine](https://img.shields.io/badge/stack_overflow-matt_vaneseltine-888.svg?style=for-the-badge&logo=stack-overflow&logoColor=fff&color=f48024)](https://stackoverflow.com/users/7846185/matt-vaneseltine)

### 💡 Acknowledgements

_Nominally_ started as a fork of the
[python-nameparser](https://github.com/derek73/python-nameparser) package,
and has benefitted considerably from this origin⸺especially the wealth of examples and tests developed for python-nameparser.
