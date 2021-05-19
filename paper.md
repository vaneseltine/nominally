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
`Nominally` simplifies and parses a single-string personal name of
[Western name order](https://en.wikipedia.org/wiki/Personal_name#Name_order)
into six core fields: title, first, middle, last, suffix, and nickname.
Typically, `nominally` is used to parse entire lists or of names en masse.

# Statement of Need

`Nominally` is a user-friendly Python package designed for name parsing
independent of any website or data science framework.
Its API provides simple command-line, function, and class access
and easily integrates with the [Pandas](https://pandas.pydata.org/) data analysis library.

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

Cumulative variations and errors combine to make
the seemingly straightforward job of finding first and last names difficult.
`Nominally` is designed to consistently extract the most useful features of personal names
under the highly restrictive case where only a single string name field is available,
and it will also perform well if name fields are concatenated.
`Nominally` aggressively cleans input;
scrapes titles, nicknames, and suffixes;
and parses apart first, middle, and last names.

`Nominally` is designed for large-scale work, and it is employed in the construction of the UMETRICS dataset [@UMETRICS2020], where millions of employee, principal investigator, and author name records are processed. This multi-university administrative dataset which has been used by over two hundred social science researchers [@IRIS2021].

TODO: Comparisons

# Examples

In the simplest case, `nominally` can parse one name string into segmented name fields:

```python
>>> from nominally import parse_name
>>> parse_name("Blankinsop, Jr., Mr. James 'Jimmy'")
{'title': 'mr', 'first': 'james', 'middle': '', 'last': 'blankinsop', 'suffix': 'jr', 'nickname': 'jimmy'}
```

`Nominally` resolves the following variations on a single name resolve into reasonably useful fields:

| Input                            | Title | First  | Middle  | Last    | Suffix | Nickname |
| -------------------------------- | ----- | ------ | ------- | ------- | ------ | -------- |
| R.J. CANNING JUNIOR              |       | r      | j       | canning | junior |          |
| Canning, Ramsay J.               |       | ramsay | j       | canning |        |          |
| Ramsay "R.J." Jackson Canning    |       | ramsay | jackson | canning |        | r j      |
| Dr. Ramsay Jackson Canning, M.D. | dr    | ramsay | jackson | canning | md     |          |
| Ramsay J. Canning, Jr.           |       | ramsay | j       | canning | jr     |          |
| canning, jr., dr. ramsay         | dr    | ramsay |         | canning | jr     |          |

# Acknowledgements

Thanks to staff of the Institute for Research on Innovation and Science at the University of Michigan, who have run `nominally` at scale and provided bug reports. Thanks go also to other human name parsing projects including [probablepeople](https://github.com/datamade/probablepeople), [name-cleaver](https://github.com/sunlightlabs/name-cleaver), and especially [python-nameparser](https://github.com/derek73/python-nameparser), the test database of which spurred `nominally`'s original fork.

# References
