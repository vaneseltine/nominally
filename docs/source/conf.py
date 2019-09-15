# https://www.sphinx-doc.org/en/master/usage/configuration.html

import re
import sys
from pathlib import Path

project = "nominally"
author = "Matt VanEseltine"
copyright = "2019, Matt VanEseltine"
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os


PROJECT_ROOT = Path("../../").resolve()
sys.path.insert(0, PROJECT_ROOT)


def get_module_version():
    path = PROJECT_ROOT / "nominally/__init__.py"
    VERSION_PATTERN = r'__version__[ ="]+?(\d+\.\d+\.[0-9a-z_-]+)'
    text = Path(path).read_text()
    result = re.search(VERSION_PATTERN, text)
    if not result:
        return f"Failed to find version in {path}"
    return result.group(1)


# The full version, including alpha/beta/rc tags
release = get_module_version()


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

intersphinx_timeout = 10


autodoc_default_options = {
    "ignore-module-all": True,
    "autodoc_member_order": "bysource",
}
# Does not appear to be working
autodoc_member_order = "bysource"


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "alabaster"
html_theme = "sphinx_rtd_theme"  # pip install sphinx_rtd_theme


# A Windows icon file (.ico) 16x16 or 32x32 pixels large.
# html_favicon = "./_static/favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_theme_options = {
    "style_external_links": False,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "prev_next_buttons_location": "both",
}

html_show_sphinx = False
