<h2>nominally is an opinionated name parser for record linkage.</h2>

[![License: AGPL 3.0](https://img.shields.io/pypi/l/nominally.svg?style=flat-square&color=violet)](https://www.gnu.org/licenses/agpl-3.0)
[![Python: 3.6+](https://img.shields.io/pypi/pyversions/nominally.svg?&style=flat-square)](https://pypi.python.org/pypi/nominally)
[![GitHub last commit](https://img.shields.io/github/last-commit/vaneseltine/nominally.svg?style=flat-square)](https://git.sr.ht/~matvan/nominally)

### 🎓 Origins

**nominally** draws on the work and test bank implemented in python-nameparser
into a simpler, more opinionated form.

The key benefit is that **nominally** narrowly maximizes on parsing
lists of decently well-formed single name fields. Therefore, **nominally**
does *not* support:

- Mutability
- Easy customization of lists of name parts
- Parsing multiple names from a single field
- Most titles, profession names, etc.
- Mononyms; i.e., input names expected to output only a single field
- Encoding other than UTF-8
- Input from byte strings
- Python < 3.6


Whereas I gain:

1. Easier maintainability (relative to keeping a closer fork).
2. Improved testing suite (via pytest).
3. Improved formatting (flake8, black across the board).

<!--

### To consider

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
    nominally\__init__.py:17: note:     <1 more non-matching overload not shown> -->


### 🧙‍ Author

[![Matt VanEseltine](https://img.shields.io/badge/name-matt_vaneseltine-888.svg?style=for-the-badge&logo=linux&logoColor=fff&color=violet)](https://vaneseltine.github.io)

[![matvan@umich.edu](https://img.shields.io/badge/email-matvan@umich.edu-888.svg?style=for-the-badge&logo=gmail&logoColor=fff&color=00274c)](mailto:matvan@umich.edu)

[![https://git.sr.ht/~matvan](https://img.shields.io/badge/sr.ht-matvan-888.svg?style=for-the-badge&color=007bff&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QIGCC8n92KyhQAAAj1QTFRFAAAA////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////anIwUQAAAL50Uk5TAAECAwQFBgcICQoLDA4PEBESExQVFhcYGRobHB0eHyAhIyQmJygpKistLzAzNDU2Nzg5Ozw9QEFDREZHSElLTE1OT1BRVFdYWVpbXF1eX2BhZGZnaGltbnBxdHV3eHp7fn+AgYKDhIWGh4iJio2TlJucnqGio6Smp6ipqqusrbCxsrO0tre4ury9vr/Cw8TFxsfIycrMzc7P0dLT1dbY2dvf4OLj5OXm5+jq6+zt7u/w8fL09fb3+Pn6+/z9/gNzyOkAAAABYktHRL6k3IPDAAAFwUlEQVQYGe3B+VtUVQAG4G9i0TQZZyA1S0JxydzDNFTUqXBfcylzS8UE21TMyjAQUQnFEi0BHQU3cAc0UGbm+9v65Zw7y70zc++dc3qenof3xZAhQ4b8T+V/uGn/kdrm1psdHTdbm2uP7Ns434//yLD5e+u7aOH+6T0ludBszGf1L5jC87rNBdDm9XXnw0wrfG71cOhQ9N0z2vTk20Ko9t5PYToQOj4FKr17IkKHwtUToMobVQN0of/rkVDik7t06c5yZC7/V1rqajq6f9vKQFlZYNW2A0cvdNPSL35kaPEDmgxerFiSjwQFZQebQzTpKkUmsg4xUX/Nijwk4V15aoAJIhVZcM13ngnatuQhJe/WNiY464VLE28xXsMCD9LyLDzLeMEiuDLzIeM0zIRNs88xTvcMuFDSx1htC+FA6XXG6pkLx0qeM8aLHdlwJGfnP4zRNw8OzexjjOaJcGzSn4zR8z4cmfiQUZF9WXAhuyLCqO4iOOC7xahni+BSWQ+jgl7YlnWeUR3FcG1qJ6MasmDXIUZdexMZGNvGqAOwaTGjrnqREd/fNERKYUvBAxqueZEhXzsNXX7Y8SsNHW8iY+M6afgZNnxKw7NiKDCtl4YA0nrjHqXIIiixjIY7I5FOFQ37oEglDZVIo+glpeYsKJJ9mdJAIVI7QenFRChT3E+pGim9F6G0AwrtohSeglR+otSWDYVygpSqkUJRmNJCKLWEUmgCkvuOUgPU8vxO6TCSev0ZpZlQ7ANKj4YhmXWUGqBcI6UVSOY8pQVQbhGlM0hiTJhCmwfKeW5QCPlh7TNKW6DBdkobYa2eQn8eNPC9pPAbLA17QaEGWtRS6MuBlfmUVkCLtZTmwspeCoN50MIXprATVuopXIQmLRROwUoXhQpoUkXhNizkU1oCTZZRyoPZh5Tyock4SnNgtolCF3TxPKKwBmb7KTRBm0sUdsPsCIWj0OY4hR9gVkthP7SppHASZs0UtkGbLyg0wqyVwkpos4FCC8xuUghAm3IK7TDroFAGbQIUgjDroFAGbQIUgjC7SSEAbcoptMOslcIqaLOBQgvMmilsgzY7KDTCrJbCAWhTReEkzI5QOAptfqTwPcz2UbgAbS5R2AWzjRS6oYvnMYXVMJtPqQCavEVpNsz8lMqgyXJKo2DhPoWD0OQwhU5YOU2hGZpcoVADK3sohLzQwh+h8CWslFBaCS3WUZoDK7nPKZyCFnUUerNh6TSFAS808L+iUANrmylthQafU1oPawVhCm0eKOcJUhgcjSTOUVoI5RZTqkMyqymdhXJNlMqRzPAnlGZDsRJKD3OR1LeUzkEtTxOlSiRXGKL0EZRaSmlwPFI4Tul6DhTKvUXpGFKZEqa0EwrtoRQqRkrVlP6ZBGUmD1A6htQm9FP6IxuK5Fyl1P8O0viahgoo8g0NB5HOyDuUImVQ4mMabo9AWgEaeqZCgel9NCyFDb/Q0DkWGXv7Lg0nYIe/i4Y2HzKUf4OGe6NhS2mEhr98yEh+Kw3hBbCpglHt45CB8TcY9RXsyjrLqM5pcG36XUadfg22eYOM6l0Glz7uY9T1UXCg6AFjHMqGCznfMMb9Qjgyo4cxLhfDsclXGePpdDg0r48x+nflwJHcPQOM0TsLjs3rYazgEtjnWXqLsZ7Oggszuhnn9w9gU0kT49yfDleKgozXuMiDtDyLmxjveiFc8jYwwY3tPqTk/zzIBPWj4FpWRYQJXtau9SEJ/7q6V0wQ/uo1ZKK0iybhlqplYxHP89byw1ciNLm3ABny/0xLjy4dr/xiQ3kgUL5hR9WPlx7T0onRyFzgDl26vRRKjKwcoAv9B0dAlcLqMB0KH3sHKk2pDtGBwWPFUG3C4Ue06WHleOgwbMWZENMarCvPhTb+jb/1MYXemvWjoVnO3J2nbtNCZ82Xc7LxH8mbs2b3DycbW9qDwfaWxpPf71o9exSGDBky5P/pX9F6dsCMuJp+AAAAAElFTkSuQmCC)](https://github.com/vaneseltine/nominally)

[![https://github.com/vaneseltine](https://img.shields.io/badge/github-vaneseltine-888.svg?style=for-the-badge&logo=github&logoColor=fff&color=2b3137)](https://github.com/vaneseltine)

[![https://twitter.com/vaneseltine](https://img.shields.io/badge/twitter-@vaneseltine-blue.svg?style=for-the-badge&logo=twitter&logoColor=fff&color=1da1f2)](https://twitter.com/vaneseltine)

[![https://stackoverflow.com/users/7846185/matt-vaneseltine](https://img.shields.io/badge/stack_overflow-matt_vaneseltine-888.svg?style=for-the-badge&logo=stack-overflow&logoColor=fff&color=f48024)](https://stackoverflow.com/users/7846185/matt-vaneseltine)
