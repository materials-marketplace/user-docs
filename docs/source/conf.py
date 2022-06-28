"""Configuration file for the Sphinx documentation builder."""
from utils import get_api, source_read_handler, version

# Project information
project = "MarketPlace"
copyright = "2022, all rights reserved"
author = "The MarketPlace Consortium"
release = version


def setup(app):
    app.connect("builder-inited", get_api)
    app.connect("source-read", source_read_handler)


# General configuration
extensions = [
    "myst_parser",  # markdown source
    "sphinx.ext.autodoc",  # API ref
    "sphinx.ext.napoleon",  # API ref Google and NumPy style
    "sphinx.ext.viewcode",  # API link to source
    "sphinx.ext.graphviz",
    "sphinxcontrib.plantuml",
    "sphinx_copybutton",  # Copy button for codeblocks
    "nbsphinx",  # Jupyter
    "IPython.sphinxext.ipython_console_highlighting",  # nb syntax highlight
    "sphinx.ext.autosectionlabel",  # Auto-generate section labels.
    "sphinx_panels",  # Panels in a grid layout or as drop-downs
    "sphinx_markdown_tables",
    "sphinxcontrib.redoc",  # Render OpenAPI with redoc
]

master_doc = "index"

plantuml = "java -jar lib/plantuml.jar"
plantuml_output_format = "svg_img"

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
]

# HTML output
html_theme = "sphinx_book_theme"
html_logo = "_static/img/logo_dark.png"
html_favicon = "_static/img/favicon.png"
html_theme_options = {
    "github_url": "https://github.com/Materials-MarketPlace/user-docs",
    "repository_url": "https://github.com/Materials-MarketPlace/user-docs",
    "use_repository_button": True,
    "repository_branch": "main",
    "path_to_docs": "docs",
    "logo_only": True,
    "show_navbar_depth": 2,
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Redoc configuration (openAPI)
redoc = [
    {
        "name": "MarketPlace API",
        "page": "apps/api",
        "spec": "apps/openAPI.json",
        "embed": True,
        "opts": {
            "suppress-warnings": True,
        },
    },
]

# LaTeX output
# (startdocname, targetname, title, author, theme, toctree_only)
latex_documents = [
    (
        "index",
        "marketplace_docs.tex",
        "MarketPlace Docs",
        "The MarketPlace Consortium",
        "manual",
        "false",
    )
]
latex_logo = "_static/img/logo_dark.png"
latex_elements = {"figure_align": "H"}

# Notebook configuration
nbsphinx_allow_errors = True
