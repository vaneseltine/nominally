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

### 🖥️ Examples

Run a quick name at the command line:
```
$ nominally "Jimmy Blankinsop"
       raw: Jimmy Blankinsop
   cleaned: jimmy blankinsop
    parsed: blankinsop, jimmy
      list: ['', 'jimmy', '', 'blankinsop', '', '']
     title:
     first: jimmy
    middle:
      last: blankinsop
    suffix:
  nickname:
```
Pull out the major parts...
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
Or separate into individual parts; complete string; lists; dicts...
```
$ python -q
>>> from nominally import Name
>>> n = Name("DR. PEACHES BARTKOWICZ")
>>> n
Name({'title': 'dr', 'first': 'peaches', 'middle': '', 'last': 'bartkowicz', 'suffix': '', 'nickname': ''})
>>> str(n)
'dr peaches bartkowicz'
>>> dict(n)
{
  'title': 'dr',
  'first': 'peaches',
  'middle': '',
  'last': 'bartkowicz',
  'suffix': '',
  'nickname': ''
}
>>> list(n.values())
['dr', 'peaches', '', 'bartkowicz', '', '']
>>> n.first
'peaches'
>>> n.last
'bartkowicz'
>>> n.raw
'DR. PEACHES BARTKOWICZ'
>>> n.report()
{
  'raw': 'DR. PEACHES BARTKOWICZ',
  'cleaned': 'dr peaches bartkowicz',
  'parsed': 'bartkowicz, dr peaches',
  'list': ['dr', 'peaches', '', 'bartkowicz', '', ''],
  'title': 'dr',
  'first': 'peaches',
  'middle': '',
  'last': 'bartkowicz',
  'suffix': '',
  'nickname': ''
}
```

### 🔬 Elaborate Examples

For fully worked examples, see:
https://github.com/vaneseltine/nominally-examples/

### 🧙‍ Author

[![Matt VanEseltine](https://img.shields.io/badge/name-matt_vaneseltine-888.svg?style=for-the-badge&logo=linux&logoColor=fff&color=violet)](https://vaneseltine.github.io)

[![matvan@umich.edu](https://img.shields.io/badge/email-matvan@umich.edu-888.svg?style=for-the-badge&logo=gmail&logoColor=fff&color=00274c)](mailto:matvan@umich.edu)

[![https://git.sr.ht/~matvan](https://img.shields.io/badge/sr.ht-matvan-888.svg?style=for-the-badge&color=007bff&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QIGCC8n92KyhQAAAj1QTFRFAAAA////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////anIwUQAAAL50Uk5TAAECAwQFBgcICQoLDA4PEBESExQVFhcYGRobHB0eHyAhIyQmJygpKistLzAzNDU2Nzg5Ozw9QEFDREZHSElLTE1OT1BRVFdYWVpbXF1eX2BhZGZnaGltbnBxdHV3eHp7fn+AgYKDhIWGh4iJio2TlJucnqGio6Smp6ipqqusrbCxsrO0tre4ury9vr/Cw8TFxsfIycrMzc7P0dLT1dbY2dvf4OLj5OXm5+jq6+zt7u/w8fL09fb3+Pn6+/z9/gNzyOkAAAABYktHRL6k3IPDAAAFwUlEQVQYGe3B+VtUVQAG4G9i0TQZZyA1S0JxydzDNFTUqXBfcylzS8UE21TMyjAQUQnFEi0BHQU3cAc0UGbm+9v65Zw7y70zc++dc3qenof3xZAhQ4b8T+V/uGn/kdrm1psdHTdbm2uP7Ns434//yLD5e+u7aOH+6T0ludBszGf1L5jC87rNBdDm9XXnw0wrfG71cOhQ9N0z2vTk20Ko9t5PYToQOj4FKr17IkKHwtUToMobVQN0of/rkVDik7t06c5yZC7/V1rqajq6f9vKQFlZYNW2A0cvdNPSL35kaPEDmgxerFiSjwQFZQebQzTpKkUmsg4xUX/Nijwk4V15aoAJIhVZcM13ngnatuQhJe/WNiY464VLE28xXsMCD9LyLDzLeMEiuDLzIeM0zIRNs88xTvcMuFDSx1htC+FA6XXG6pkLx0qeM8aLHdlwJGfnP4zRNw8OzexjjOaJcGzSn4zR8z4cmfiQUZF9WXAhuyLCqO4iOOC7xahni+BSWQ+jgl7YlnWeUR3FcG1qJ6MasmDXIUZdexMZGNvGqAOwaTGjrnqREd/fNERKYUvBAxqueZEhXzsNXX7Y8SsNHW8iY+M6afgZNnxKw7NiKDCtl4YA0nrjHqXIIiixjIY7I5FOFQ37oEglDZVIo+glpeYsKJJ9mdJAIVI7QenFRChT3E+pGim9F6G0AwrtohSeglR+otSWDYVygpSqkUJRmNJCKLWEUmgCkvuOUgPU8vxO6TCSev0ZpZlQ7ANKj4YhmXWUGqBcI6UVSOY8pQVQbhGlM0hiTJhCmwfKeW5QCPlh7TNKW6DBdkobYa2eQn8eNPC9pPAbLA17QaEGWtRS6MuBlfmUVkCLtZTmwspeCoN50MIXprATVuopXIQmLRROwUoXhQpoUkXhNizkU1oCTZZRyoPZh5Tyock4SnNgtolCF3TxPKKwBmb7KTRBm0sUdsPsCIWj0OY4hR9gVkthP7SppHASZs0UtkGbLyg0wqyVwkpos4FCC8xuUghAm3IK7TDroFAGbQIUgjDroFAGbQIUgjC7SSEAbcoptMOslcIqaLOBQgvMmilsgzY7KDTCrJbCAWhTReEkzI5QOAptfqTwPcz2UbgAbS5R2AWzjRS6oYvnMYXVMJtPqQCavEVpNsz8lMqgyXJKo2DhPoWD0OQwhU5YOU2hGZpcoVADK3sohLzQwh+h8CWslFBaCS3WUZoDK7nPKZyCFnUUerNh6TSFAS808L+iUANrmylthQafU1oPawVhCm0eKOcJUhgcjSTOUVoI5RZTqkMyqymdhXJNlMqRzPAnlGZDsRJKD3OR1LeUzkEtTxOlSiRXGKL0EZRaSmlwPFI4Tul6DhTKvUXpGFKZEqa0EwrtoRQqRkrVlP6ZBGUmD1A6htQm9FP6IxuK5Fyl1P8O0viahgoo8g0NB5HOyDuUImVQ4mMabo9AWgEaeqZCgel9NCyFDb/Q0DkWGXv7Lg0nYIe/i4Y2HzKUf4OGe6NhS2mEhr98yEh+Kw3hBbCpglHt45CB8TcY9RXsyjrLqM5pcG36XUadfg22eYOM6l0Glz7uY9T1UXCg6AFjHMqGCznfMMb9Qjgyo4cxLhfDsclXGePpdDg0r48x+nflwJHcPQOM0TsLjs3rYazgEtjnWXqLsZ7Oggszuhnn9w9gU0kT49yfDleKgozXuMiDtDyLmxjveiFc8jYwwY3tPqTk/zzIBPWj4FpWRYQJXtau9SEJ/7q6V0wQ/uo1ZKK0iybhlqplYxHP89byw1ciNLm3ABny/0xLjy4dr/xiQ3kgUL5hR9WPlx7T0onRyFzgDl26vRRKjKwcoAv9B0dAlcLqMB0KH3sHKk2pDtGBwWPFUG3C4Ue06WHleOgwbMWZENMarCvPhTb+jb/1MYXemvWjoVnO3J2nbtNCZ82Xc7LxH8mbs2b3DycbW9qDwfaWxpPf71o9exSGDBky5P/pX9F6dsCMuJp+AAAAAElFTkSuQmCC)](https://github.com/vaneseltine/nominally)

[![https://github.com/vaneseltine](https://img.shields.io/badge/github-vaneseltine-888.svg?style=for-the-badge&logo=github&logoColor=fff&color=2b3137)](https://github.com/vaneseltine)

[![https://twitter.com/vaneseltine](https://img.shields.io/badge/twitter-@vaneseltine-blue.svg?style=for-the-badge&logo=twitter&logoColor=fff&color=1da1f2)](https://twitter.com/vaneseltine)

[![https://stackoverflow.com/users/7846185/matt-vaneseltine](https://img.shields.io/badge/stack_overflow-matt_vaneseltine-888.svg?style=for-the-badge&logo=stack-overflow&logoColor=fff&color=f48024)](https://stackoverflow.com/users/7846185/matt-vaneseltine)

### 🎓 Beginnings

**Nominally** started as a fork of the
[python-nameparser](https://github.com/derek73/python-nameparser) package,
and has benefitted considerably from this origin⸺especially the
testing foundation.
