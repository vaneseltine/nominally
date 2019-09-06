**nominally** aims to condense, narrow, and reduce the system originally
implemented in python-nameparser into a simpler, more opinionated form.

The key benefit is that **nominally** narrowly maximizes on parsing
lists of decently well-formed single name fields. Therefore, **nominally**
does *not* support:

- Mutability
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

#### Allow for 'y' and 'e' conjunctions within last names

#### Confirm `r'[a-z]'` on each part to make, e.g., Name("#") unparsable

#### Fix typing

`dict(Name())`

    nominally\__init__.py:15: error: No overload variant of "dict" matches argument type "Name"
    nominally\__init__.py:15: note: Possible overload variants:
    nominally\__init__.py:15: note:     def [_KT, _VT] __init__(self, map: Mapping[_KT, _VT], **kwargs: _VT) -> Dict[_KT, _VT]
    nominally\__init__.py:15: note:     def [_KT, _VT] __init__(self, iterable: Iterable[Tuple[_KT, _VT]], **kwargs: _VT) -> Dict[_KT, _VT]
    nominally\__init__.py:15: note:     <1 more non-matching overload not shown>
    nominally\__init__.py:15: note:     def [_KT, _VT] __init__(self, map: Mapping[_KT, _VT], **kwargs: _VT) -> Dict[_KT, _VT]
    nominally\__init__.py:15: note:     def [_KT, _VT] __init__(self, iterable: Iterable[Tuple[_KT, _VT]], **kwargs: _VT) -> Dict[_KT, _VT]

`list(Name())`

    nominally\__init__.py:17: error: No overload variant of "list" matches argument type "Name"
    nominally\__init__.py:17: note: Possible overload variant:
    nominally\__init__.py:17: note:     def [_T] __init__(self, iterable: Iterable[_T]) -> List[_T]
    nominally\__init__.py:17: note:     <1 more non-matching overload not shown>