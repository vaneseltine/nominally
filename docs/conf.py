# https://www.sphinx-doc.org/en/master/usage/configuration.html

import re
import sys
from pathlib import Path

import alabaster

project = "nominally"
author = "Matt VanEseltine"
copyright = "2019, Matt VanEseltine"

PROJECT_ROOT = Path("../").resolve()
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


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_autorun",
]

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
intersphinx_timeout = 10

autodoc_member_order = "bysource"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

html_theme_path = [alabaster.get_path()]
extensions += ["alabaster"]
html_theme = "alabaster"

# A Windows icon file (.ico) 16x16 or 32x32 pixels large.
html_favicon = "./_static/favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_theme_options = {
    "fixed_sidebar": True,
    "logo": "nominally_logo.png",
    "logo_name": True,
    "logo_text_align": "center",
    "show_related": False,
    "description": "A maximum-strength name parser for record linkage",
    "github_button": True,
    "github_type": "star",
    "github_user": "vaneseltine",
    "github_repo": "nominally",
    "github_count": False,
    "show_powered_by": True,
    "show_relbars": True,
}
html_show_sphinx = False
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        "donate.html",
    ]
}
