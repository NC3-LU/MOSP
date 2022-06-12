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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
# -- Project information -----------------------------------------------------

project = "MOSP"
copyright = "SECURITYMADEIN.LU <info@cases.lu>"
author = "Cédric Bonhomme <cedric@cedricbonhomme.org>"

# The full version, including alpha/beta/rc tags
release = "0.13.0"


# -- General configuration ---------------------------------------------------

master_doc = "index"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx_multiversion",
]

# Patterns
# smv_tag_whitelist = r"^refs/tags/v\d+\.\d+\.\d+$|latest"
smv_released_pattern = r"^refs/tags/v\d+\.\d+\.\d+$"
# smv_branch_whitelist = r'master$'
smv_branch_whitelist = r"^(?!translations).*$"
smv_remote_whitelist = None


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

html_sidebars = {
    "**": [
        "sbt-sidebar-nav.html",
        "versioning.html",
    ],
}


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

numfig = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"

html_sidebars = {
    "**": [
        "sbt-sidebar-nav.html",
        "versioning.html",
    ],
}

html_theme_options = {
    "theme_dev_mode": True,
    "path_to_docs": "docs",
    "repository_url": "https://github.com/CASES-LU/MOSP",
    # "repository_branch": "gh-pages",  # For testing
    "launch_buttons": {
        "binderhub_url": "https://github.com/CASES-LU/MOSP",
    },
    "use_edit_page_button": True,
    "use_issues_button": True,
    "use_repository_button": True,
    "use_download_button": True,
    # For testing
    # "use_fullscreen_button": False,
    # "home_page_in_toc": True,
    # "single_page": True,
    # "extra_footer": "<a href='https://google.com'>Test</a>",  # DEPRECATED KEY
    # "extra_navbar": "<a href='https://google.com'>Test</a>",
    # "show_navbar_depth": 2,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
