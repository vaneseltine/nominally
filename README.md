**nominally** aims to condense, narrow, and reduce the system originally
implemented in python-nameparser into a simpler, more opinionated form.

The key benefit is that **nominally** narrowly maximizes on parsing
lists of decently well-formed single name fields. Therefore, **nominally**
does *not* support:

- Mutability of HumanName
- Easy customization of lists of name parts
- Parsing multiple names from a single field
- Most titles
- Mononyms; i.e., input names expected to output only a single field
- Encoding other than UTF-8
- Input from byte strings
- Python < 3.6

<!-- Della, Abu, Doctor... -->

Whereas I gain:

1. Easier maintainability (relative to keeping a closer fork).
2. Improved testing suite (via pytest).
3. Improved formatting (flake8, black across the board).

## To consider

- Allow for 'y' and 'e' conjunctions within last names
- Expand Md.
- Confirm `r'[a-z]'` on each part to make, e.g., HumanName("#") unparsable
