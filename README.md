**nominally** aims to condense, narrow, and reduce the system originally
implemented in python-nameparser into a simpler, more opinionated form.

The key benefit is that **nominally** narrowly maximizes on parsing
lists of decently well-formed single name fields. Therefore, **nominally**
does *not* support:

1. Easy customization of lists of name parts
2. Parsing multiple names from a single field
3. Lengthy and carefully curated built-in titles for many occasions
4. Encoding other than UTF-8
5. Very much extensibility
6. Python < 3.6

<!-- Della, Abu, Doctor... -->

Whereas I gain:

1. Easier maintainability (relative to keeping a closer fork).
2. Improved testing suite (via pytest).
3. Improved formatting (flake8, black across the board).
