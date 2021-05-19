---
title: "Nominally: A Name Parser for Record Linkage"
tags:
  - Python
  - data science
  - record linkage
  - entity resolution
  - name parsing
authors:
  - name: Matthew VanEseltine
    orcid: 0000-0002-9520-1360
    affiliation: 1
affiliations:
  - name: Institute for Social Research, University of Michigan
    index: 1
date: May 2021
bibliography: paper.bib
---

# Summary

Increasing availability to data in recent decades has heightened the importance
of successfully connecting people across disparate datasets through record linkage.
As we draw from multiple data sources,
we would like identify and measure similarities of the name
"Matthew VanEseltine" in one database,
"Matt Van Eseltine" in another,
and "Vaneseltine, M PhD" in a third.
`Nominally` is designed to assist in the initial stages of record linkage,
where datasets are cleaned and preprocessed.
It uses a rule-based system [@Christen2012]
to simplify and parse a single-string personal name
of [Western name order](https://en.wikipedia.org/wiki/Personal_name#Name_order)
into six core fields: title, first, middle, last, suffix, and nickname.

# Statement of Need

`Nominally` is a user-friendly Python package designed for name parsing
independent of any specific data science framework or website
and requiring minimal dependencies.
Its API provides simple command-line, function, and class access
and easily integrates with the [Pandas](https://pandas.pydata.org/) data analysis library.
The typical use case of `nominally` is parsing entire lists of names en masse.

Human names can be difficult to work with in data.
Varying quality and practices across institutions and datasets introduce noise
into data and cause misrepresentation. This increases the challenges of
deduplicating rows within data and and linking names across multiple datasets.
Errors and discrepencies easily include (and this list is by no means exhaustive):

- First and middle names split arbitrarily.
- Misplaced prefixes of last names (e.g., "van" and "de la").
- Records with multiple last names partitioned into middle name fields.
- Titles and suffixes variously recorded in different fields and with or without separators.
- Inconsistent capture of accents and other non-ASCII characters.
- Single name fields arbitrarily concatenating name parts.

Cumulative variations and errors can combine to make
the seemingly straightforward job of simply identifying first and last names rather difficult.
`Nominally` is designed to consistently extract the most useful features of personal names
without assuming any prior differentiation between name fields.
That is, it works under the highly restrictive case where only a single string name field is available,
and it will thereby perform well if existing name fields are concatenated.
`Nominally` aggressively cleans input;
scrapes titles, nicknames, and suffixes;
and parses apart first, middle, and last names.

`Nominally` is designed for large-scale work,
and we employ `nominally` as part of the construction of data linkage for
the UMETRICS dataset at the Institute for Research on Innovation & Science [@UMETRICS2020],
which requires processing millions of
university employee, grant principal investigator, and journal author name records.

Multiple open-source Python packages focus on parsing names, including
`python-nameparser` [@python-nameparser],
`probablepeople` [@probablepeople],
and `name-cleaver` [@name-cleaver].
`Nominally` improves upon these packages in its core use case:
parsing single human names in Western name order.
`Nominally` began from a fork of `python-nameparser`,
initially aiming to refactor code and improve certain test cases.
As development continued through a complete overhaul,
the current core state of `nominally` accurately handles a wider range of names.
`Probablepeople` and `name-cleaver`
both extend their processes to simultaneously address
capturing the details of multiple names, politicians, or companies.
By narrowing the scope to single human names,
`nominally` loses the broader applications of these packages
but gains accuracy in this core capacity.

# Examples

In its simplest application,
`nominally` can parse one name string into a dictionary of segmented name fields:

```python
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

The possible combinations of name parts are too extensive to present,
but as a further example `nominally` extracts appropriate and comparable fields
from these divergent presentations of a single name:

| Input                          | Title | First  | Middle | Last  | Suffix | Nickname |
| ------------------------------ | ----- | ------ | ------ | ----- | ------ | -------- |
| S.T. VIMES JUNIOR              |       | s      | t      | vimes | jr     |          |
| Vimes, Samuel T.               |       | samuel | t      | vimes |        |          |
| samüél t vimés                 |       | samuel | t      | vimes |        |          |
| Samuel "sam" Thomas Vimes      |       | samuel | thomas | vimes |        | sam      |
| Dr. Samuel Thomas Vimes, Ph.D. | dr    | samuel | thomas | vimes | phd    |          |
| Samuel T. Vimes, Jr. 24601     |       | samuel | t      | vimes | jr     |          |
| vimes, jr. phd, samuel         |       | samuel |        | vimes | jr phd |          |

# Acknowledgements

Special thanks go to IRIS staff at the University of Michigan,
who have run `nominally` at scale and provided bug reports.
`Nominally` is indebted to the foundation of the
[python-nameparser](https://github.com/derek73/python-nameparser) project;
its base of tests and name lists have been
especially helpful throughout `nominally`'s development.

# References
