---
title: "nominally: a name parser for record linkage"
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
As we draw from multiple data sources, we would like to identify
"Matthew VanEseltine" in one database
as the same individual as "Matt Van Eseltine" in another
and "Vaneseltine, M PhD" in a third.
`Nominally` is designed to assist in the initial stages of record linkage across datasets,
during cleaning and preprocessing.
It uses a rule-based process [@Christen2012]
to simplify and parse a single-string personal name of
[Western name order](https://en.wikipedia.org/wiki/Personal_name#Name_order)
into six core fields: title, first, middle, last, suffix, and nickname.
The typical use case of `nominally` is parsing entire lists of names en masse.

# Statement of Need

`Nominally` is a user-friendly Python package designed for name parsing
independent of any specific data science framework or website
and requiring minimal dependencies.
Its API provides simple command-line, function, and class access
and easily integrates with the [Pandas](https://pandas.pydata.org/) data analysis library.

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

`Nominally` is designed for large-scale work, and we employ `nominally` in the construction of UMETRICS data at the Institute for Research on Innovation & Science [@UMETRICS2020], where millions of employee, principal investigator, and author name records are processed. UMETRICS is a multi-university administrative dataset used by over two hundred social science researchers in recent years [@IRIS2021].

TODO: Comparisons

# Examples

In its simplest application, `nominally` can parse one name string into a dictionary of segmented name fields:

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
but as a further example `Nominally` extracts appropriate and comparable fields
from these divergent presentations of a single name:

| Input                          | Title | First  | Middle | Last  | Suffix | Nickname |
| ------------------------------ | ----- | ------ | ------ | ----- | ------ | -------- |
| S.T. VIMES JUNIOR              |       | s      | t      | vimes | jr     |
| Vimes, Samuel T.               |       | samuel | t      | vimes |        |
| samüél t vimés                 |       | samuel | t      | vimes |        |
| Samuel "sam" Thomas Vimes      |       | samuel | thomas | vimes |        | sa       |
| Dr. Samuel Thomas Vimes, Ph.D. | dr    | samuel | thomas | vimes | phd    |
| Samuel T. Vimes, Jr.           |       | samuel | t      | vimes | jr     |
| vimes, jr. phd, samuel         |       | samuel |        | vimes | jr phd |

# Acknowledgements

Thanks to IRIS staff at the University of Michigan,
who have run `nominally` at scale and provided bug reports.
Thanks go also to other human name parsing projects including
[probablepeople](https://github.com/datamade/probablepeople),
[name-cleaver](https://github.com/sunlightlabs/name-cleaver),
and especially [python-nameparser](https://github.com/derek73/python-nameparser).
Before considerable overhaul, `nominally` began life as a fork of `python-nameparser`,
and working with its test name lists was very helpful through `nominally`'s development.

# References
