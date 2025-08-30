# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from glow import __version__ as full_version

project = "glow"
copyright = "2025, aatroxfly"
author = "aatroxfly"
version = full_version.split("+")[0]
release = ".".join(version.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_removed_in",
    "sphinxcontrib_trio",
    "sphinxcontrib.towncrier.ext",  # provides `towncrier-draft-entries` directive
    "sphinx_issues",  # implements `:issue:`, `:pr:` and other GH-related roles
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "zh_CN"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
