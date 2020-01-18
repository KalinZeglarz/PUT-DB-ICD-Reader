# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

sys.path.insert(0, os.path.abspath('../../icd_mapper/'))
sys.setrecursionlimit(1500)

# -- Project information -----------------------------------------------------

project = 'ICD Mapper'
copyright = '2020, Tomasz Kiljanczyk, Juliusz Chorowski, Michal Kalinowski, Marcin Jasinski'
author = 'Tomasz Kiljanczyk, Juliusz Chorowski, Michal Kalinowski, Marcin Jasinski'

# The full version, including alpha/beta/rc tags
release = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    'autodocsumm',
    "sphinx_rtd_theme"
]
autodoc_default_options = {
    'autosummary': True
}
autodata_content = 'both'
autoclass_content = 'both'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
