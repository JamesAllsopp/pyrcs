"""
Configuration file for the Sphinx documentation builder.
"""

# Path setup ===========================================================================
import os
import sys

# If the directory is relative to the documentation root,
# use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../pyrcs'))
sys.path.insert(0, os.path.abspath('../../pyrcs/line_data'))
sys.path.insert(0, os.path.abspath('../../pyrcs/other_assets'))

# A list of modules to be mocked up.
autodoc_mock_imports = [
    'beautifulsoup4',
    'pandas',
    'requests',
    'pyhelpers>=1.2.14',
    'measurement',
    'numpy',
    'more-itertools',
    'lxml',
    'html5lib',
]

# Project information ==================================================================
import datetime
import pyrcs

# General information about the project.
project = pyrcs.__package_name_alt__
copyright = '2019-{}, {}'.format(datetime.datetime.now().year, pyrcs.__author__)

# The version info for the project
version = pyrcs.__version__  # The short X.Y version.
release = version  # The full version, including alpha/beta/rc tags.

# General configuration ================================================================
import sphinx_rtd_theme

_ = sphinx_rtd_theme.get_html_theme_path()

# Sphinx extension module names,
#   which can be extensions coming with Sphinx (named 'sphinx.ext.*') or custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.githubpages',
    'sphinx.ext.todo',
    'sphinx_rtd_theme',
]

# Enable to reference numbered figures
numfig = True
numfig_secnum_depth = 0
numfig_format = {'figure': 'Fig. %s', 'table': 'Table %s', 'code-block': 'Code Block %s'}
numfig_format_caption = {'figure': 'Fig. %s: '}

# The language for content autogenerated by Sphinx.
language = 'en'

# Patterns (relative to source directory) that match files & directories to ignore.
exclude_patterns = ['_build', '../_build', '../build']

# Whether to scan all found documents for autosummary directives and generate stub pages for each.
autosummary_generate = True

# The suffix(es) of source filenames (For multiple suffix, a list of string.
source_suffix = '.rst'  # e.g. source_suffix = ['.rst', '.md'])

# The master toctree document.
master_doc = 'index'

# Automatically documented members are sorted by source order ('bysource').
autodoc_member_order = 'bysource'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Options for HTML and HTMLHelp output =================================================
html_theme = 'sphinx_rtd_theme'  # The theme to use for HTML & HTML Help pages.

html_theme_options = {
    'collapse_navigation': False,
    'navigation_depth': 4,
}

# Source link
html_copy_source = False
html_show_sourcelink = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'  # or 'default'

# Paths containing custom static files (e.g. style sheets), relative to this directory.
html_static_path = ['_static']

# Add custom CSS
html_css_files = ['theme_overrides.css']

# Add custom JavaScript
html_js_files = ['copybutton.js']

# Output file base name for HTML help builder. Default is 'pydoc'.
htmlhelp_basename = project + 'doc'

# Options for LaTeX output =============================================================
from pygments.formatters.latex import LatexFormatter
from sphinx.highlighting import PygmentsBridge


class CustomLatexFormatter(LatexFormatter):
    def __init__(self, **options):
        super(CustomLatexFormatter, self).__init__(**options)
        self.verboptions = r"formatcom=\small"


PygmentsBridge.latex_formatter = CustomLatexFormatter

# The LaTeX engine to build the docs.
latex_engine = 'pdflatex'

# Grouping the document tree into LaTeX files
latex_documents = [
    ('index',  # source start file
     '{}.tex'.format(pyrcs.__package_name__),  # target name
     '{} Documentation'.format(pyrcs.__package_name_alt__),  # title
     pyrcs.__author__,  # author
     'manual',  # document class ['howto', 'manual', or own class]
     1  # toctree only
     ),
]

# LaTeX customization.
latex_elements = {
    'papersize': 'a4paper',  # The paper size ('letterpaper' or 'a4paper').
    'pointsize': '11pt',  # The font size ('10pt', '11pt' or '12pt').
    'pxunit': '0.25bp',
    'preamble': r'''
        \setlength{\headheight}{14pt}
        \DeclareUnicodeCharacter{229E}{\ensuremath{\boxplus}}
        \setcounter{tocdepth}{3}
        \usepackage[none]{hyphenat}
        \usepackage[document]{ragged2e}
        \usepackage[utf8]{inputenc}
        \usepackage{textcomp}
        \usepackage{amsfonts}
        \usepackage{textgreek}
        \usepackage{graphicx}
        \usepackage{svg}
        \usepackage{booktabs}
        \usepackage[sc,osf]{mathpazo}
        \linespread{1.05}
        \renewcommand{\sfdefault}{pplj}
        \IfFileExists{zlmtt.sty}
                     {\usepackage[light,scaled=1.05]{zlmtt}}
                     {\renewcommand{\ttdefault}{lmtt}}
        \let\oldlongtable\longtable
        \let\endoldlongtable\endlongtable
        \renewenvironment{longtable}
                         {\rowcolors{1}{anti-flashwhite}{white}\oldlongtable}
                         {\endoldlongtable}
        ''',
    'sphinxsetup': r'''
        %verbatimwithframe=false,
        %verbatimwrapslines=false,
        %verbatimhintsturnover=false,
        VerbatimColor={HTML}{F5F5F5},
        VerbatimBorderColor={HTML}{E0E0E0},
        noteBorderColor={HTML}{E0E0E0},
        noteborder=1.5pt,
        warningBorderColor={HTML}{E0E0E0},
        warningborder=1.5pt,
        warningBgColor={HTML}{FBFBFB},
        hmargin={0.7in,0.7in}, vmargin={1.1in,1.1in},
        ''',
    'printindex': r'''
        \IfFileExists{\jobname.ind}
                     {\footnotesize\raggedright\printindex}
                     {\begin{sphinxtheindex}\end{sphinxtheindex}}
        ''',
    'passoptionstopackages': r'\PassOptionsToPackage{svgnames}{xcolor}',
    'fvset': r'\fvset{fontsize=auto}',
    'figure_align': 'H'  # Latex figure (float) alignment
}

# The theme that the LaTeX output should use.
latex_theme = 'manual'

# Options for manual page output =======================================================


man_pages = [  # How to group the document tree into manual pages
    ('index',  # startdocname
     pyrcs.__package_name__,  # name
     '{} Documentation'.format(pyrcs.__package_name_alt__),  # description
     [pyrcs.__author__],  # authors
     1  # section
     )
]

# Options for Texinfo output ===========================================================

texinfo_documents = [  # Grouping the document tree into Texinfo files
    (master_doc,  # source start file
     pyrcs.__package_name__,  # target name
     '{} Documentation'.format(pyrcs.__package_name_alt__),  # title
     pyrcs.__author__,  # author
     pyrcs.__package_name_alt__,  # dir menu entry
     pyrcs.__description__,  # description
     'Web-scraping tool',  # category
     1  # toctree only
     ),
]
