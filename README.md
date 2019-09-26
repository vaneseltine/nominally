<p align="center">
  <img src="https://raw.githubusercontent.com/vaneseltine/nominally/master/docs/_static/nominally_logo.png" alt="Nominally Logo" width=200 />
</p>

<h2 align="center">nominally: a maximum-strength name parser for record linkage</h2>

<p align="center">
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img alt="License: AGPL 3.0+" src="https://img.shields.io/badge/license-AGPL-009999.svg?style=flat-square" /></a>
  <a href="https://pypi.python.org/pypi/nominally"><img alt="Package hosted on PyPI" src="https://img.shields.io/pypi/v/nominally?style=flat-square&color=009999" /></a>
  <a href="https://codeclimate.com/github/vaneseltine/nominally"><img alt="Code Climate maintainability" src="https://img.shields.io/codeclimate/maintainability-percentage/vaneseltine/nominally?style=flat-square"></a>
  <a href="https://circleci.com/gh/vaneseltine/nominally"><img alt="Builds at CircleCI" src="https://img.shields.io/circleci/build/github/vaneseltine/nominally?style=flat-square" /></a>
  <a href="https://coveralls.io/github/vaneseltine/nominally"><img alt="Coveralls test coverage" src="https://img.shields.io/coveralls/github/vaneseltine/nominally?style=flat-square" /></a>
  <a href="https://nominally.readthedocs.io/en/latest/"><img alt="Read the Docs (latest)" src="https://img.shields.io/readthedocs/nominally/latest?style=flat-square" /></a>
  <a href="https://github.com/vaneseltine/nominally"><img alt="GitHub commit activity" src="https://img.shields.io/github/last-commit/vaneseltine/nominally?style=flat-square" /></a>
</p>

### 🖥️ Getting Started

Call `parse_name()` to parse out six core name parts:
```
$ python -q
>>> from nominally import parse_name
>>> parse_name("Blankinsop, Jr., Mr. James 'Jimmy'")
{
  'title': 'mr',
  'first': 'james',
  'middle': '',
  'last': 'blankinsop',
  'suffix': 'jr',
  'nickname': 'jimmy'
}
```
Dive into the `Name` class to pull out a recreated string...
```
>>> from nominally import Name
>>> n = Name("DR. PEACHES BARTKOWICZ")
>>> n
Name({'title': 'dr', 'first': 'peaches', 'middle': '', 'last': 'bartkowicz', 'suffix': '', 'nickname': ''})
>>> str(n)
'bartkowicz, dr peaches'

```
...the dict, or a more elaborate set of attributes...
```
>>> dict(n)
{
  'title': 'dr',
  'first': 'peaches',
  'middle': '',
  'last': 'bartkowicz',
  'suffix': '',
  'nickname': ''
}
>>> n.report()
{
  'raw': 'DR. PEACHES BARTKOWICZ',
  'cleaned': {'dr peaches bartkowicz'},
  'parsed': 'bartkowicz, dr peaches',
  'list': ['dr', 'peaches', '', 'bartkowicz', '', ''],
  'title': 'dr',
  'first': 'peaches',
  'middle': '',
  'last': 'bartkowicz',
  'suffix': '',
  'nickname': ''
}
>>> list(n.values())
['dr', 'peaches', '', 'bartkowicz', '', '']
```
...individual attributes, and so on.
```
>>> n.first
'peaches'
>>> n['last']
'bartkowicz'
>>> n.get('title')
'dr'
>>> n.raw
'DR. PEACHES BARTKOWICZ'

```
And for a quick report, invoke the `nominally` command line tool:
```
$ nominally "DR. PEACHES BARTKOWICZ"
       raw: DR. PEACHES BARTKOWICZ
   cleaned: dr. peaches bartkowicz
    parsed: bartkowicz, dr peaches
      list: ['dr', 'peaches', '', 'bartkowicz', '', '']
     title: dr
     first: peaches
    middle:
      last: bartkowicz
    suffix:
  nickname:
```

### 🔬 Worked Examples

Binder hosts Jupyter notebooks with detailed Nominally examples:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[![csv.ipynb on mybinder.org](https://img.shields.io/badge/launch_binder-csv_parse-888.svg?style=for-the-badge&logo=jupyter&logoColor=fff&color=ff4785)](https://mybinder.org/v2/gh/vaneseltine/nominally-examples/master?filepath=notebooks%2Fcsv.ipynb)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[![pandas_simple.ipynb on mybinder.org](https://img.shields.io/badge/launch%20binder-pandas_apply-888.svg?style=for-the-badge&logo=jupyter&logoColor=fff&color=ff4785)](https://mybinder.org/v2/gh/vaneseltine/nominally-examples/master?filepath=notebooks%2Fpandas_simple.ipynb)

These notebooks and more worked examples [reside in the Nominally Examples repository](https://github.com/vaneseltine/nominally-examples/).

### 🎓 Beginnings

**Nominally** started as a fork of the
[python-nameparser](https://github.com/derek73/python-nameparser) package,
and has benefitted considerably from this origin⸺especially the wealth of examples and tests developed for python-nameparser.


### 🧙‍ Author

[![Matt VanEseltine](https://img.shields.io/badge/name-matt_vaneseltine-888.svg?style=for-the-badge&logo=linux&logoColor=fff&color=violet)](https://vaneseltine.github.io)

[![https://pypi.org/user/matvan/](https://img.shields.io/badge/pypi-matvan-888.svg?style=for-the-badge&logo=python&logoColor=fff&color=0073b7)](https://pypi.org/user/matvan/)



[![matvan@umich.edu](https://img.shields.io/badge/email-matvan@umich.edu-888.svg?style=for-the-badge&logo=gmail&logoColor=fff&color=00274c)](mailto:matvan@umich.edu)


[![https://github.com/vaneseltine](https://img.shields.io/badge/github-vaneseltine-888.svg?style=for-the-badge&logo=github&logoColor=fff&color=2b3137)](https://github.com/vaneseltine)

[![https://twitter.com/vaneseltine](https://img.shields.io/badge/twitter-@vaneseltine-blue.svg?style=for-the-badge&logo=twitter&logoColor=fff&color=1da1f2)](https://twitter.com/vaneseltine)

[![https://stackoverflow.com/users/7846185/matt-vaneseltine](https://img.shields.io/badge/stack_overflow-matt_vaneseltine-888.svg?style=for-the-badge&logo=stack-overflow&logoColor=fff&color=f48024)](https://stackoverflow.com/users/7846185/matt-vaneseltine)
