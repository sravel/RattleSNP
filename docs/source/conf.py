#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import rattleSNP
import toml
import sphinx_rtd_theme
from datetime import datetime

with open('../../pyproject.toml', 'r') as f:
    conf = toml.load(f)

# The short X.Y version.
version = rattleSNP.__version__
# The full version, including alpha/beta/rc tags
release = rattleSNP.__version__

# -- Project information -----------------------------------------------------
# General information about the project.
project = conf['project']['name']
authors = conf['project']['authors']
date = datetime.now()
copyright = "2019-{year}, S Ravel (CIRAD)".format(year=date.timetuple()[0])

# -- General configuration ---------------------------------------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = [
              'sphinx.ext.viewcode',
              'sphinx.ext.autosectionlabel',
              'sphinx_copybutton',
              "sphinx_rtd_theme",
              'sphinx_click'
              ]
gitlab_url = 'forge.ird.fr'
gitlab_user = 'PHIM/sravel'
gitlab_repo = 'forge.ird.fr'
gitlab_version = 'master'
display_gitlab = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = ['.rst', "md"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

master_doc = 'index'

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'analytics_id': '',  #  Provided by Google in your dashboard
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 3,
    'includehidden': False,
    'titles_only': False,
}

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "RattleSNP"

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = "RattleSNP"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '_images/rattleSNP_logo.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = '_images/rattleSNP-small.svg'
global html_context

html_context = {
    "gitlab_host": "forge.ird.fr",
    "display_gitlab": True, # Integrate Gitlab
    "gitlab_user": "PHIM/sravel", # Username
    "gitlab_repo": "RattleSNP", # Repo name
    "gitlab_version": "master", # Version
    "conf_py_path": "/docs/source/", # Path in the checkout to the docs root
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If false, no index is generated.
html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True
