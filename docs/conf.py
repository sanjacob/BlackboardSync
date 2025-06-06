# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from importlib.metadata import version as get_version
from importlib.metadata import PackageNotFoundError

from blackboard_sync import __about__

# -- Project information -----------------------------------------------------

project = "Blackboard Sync"
copyright = __about__.__copyright__
author = __about__.__author__

# The full version, including alpha/beta/rc tags
release = get_version("blackboardsync")
version = ".".join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'recommonmark',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.doctest',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autoclass_content = 'both'
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
    '.txt': 'markdown'
}


intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'hypothesis': ('https://hypothesis.readthedocs.io/en/latest', None),
    # 'pathlib': ('https://docs.python.org/3/library/pathlib.html', None)
}

# Make sure the target is unique
autosectionlabel_prefix_document = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'show_powered_by': False,
    'github_user': 'sanjacob',
    'github_repo': 'BlackboardSync',
    'github_banner': True,
    'show_related': False,
    'note_bg': '#FFF59C',
    'github_button': True,
    'github_type': 'star',
    'description': __about__.__summary__,
    # 'analytics_id': 'UA-109078714-2',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
