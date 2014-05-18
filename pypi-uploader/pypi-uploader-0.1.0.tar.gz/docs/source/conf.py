# -*- coding: utf-8 -*-
"""PyPI Uploader documentation build configuration file.

This file is execfile()d with the current directory set to its containing dir.

"""

import sphinx_readable_theme

import pypiuploader


# -- General configuration ----------------------------------------------------

# Defining Sphinx extension modules.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

autodoc_default_flags = [
    'members',
    'private-members',
    'show-inheritance',
]
autodoc_member_order = 'bysource'
intersphinx_mapping = {
    'python': ('http://docs.python.org/3.4', None),
    'requests': ('http://docs.python-requests.org/en/latest', None),
}

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'PyPI Uploader'
copyright = u'2014, Ignacy Sokołowski'

# The version info for the project, acts as replacement for |version| and
# |release|, also used in various other places throughout the built documents.
#
# The short X.Y version.
version = pypiuploader.__version__
# The full version, including alpha/beta/rc tags.
release = pypiuploader.__version__

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Don't display module names before objects titles, it's more readable.
add_module_names = False


# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme_path = [sphinx_readable_theme.get_html_theme_path()]
html_theme = 'readable'

# Output file base name for HTML help builder.
htmlhelp_basename = 'pypiuploaderdoc'


# -- Options for manual page output -------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        'index',
        'PyPI Uploader',
        u'PyPI Uploader Documentation',
        [u'Ignacy Sokołowski'],
        1,
    ),
]
