"""
Summary
=======
A toolkit for battery data analysis.

Accessing the Documentation
---------------------------
Documentation is accessible via Python's ``help()`` function which prints
docstrings from a package, module, function, class, etc. You can also access
the documentation by visiting the website, hosted on Read the Docs. The website
includes search functionality and more detailed examples.

"""

# Subpackages
from . import dqdv
from . import gitt
from . import plotutils
from . import utils

__version__ = '0.0.1'

__all__ = [
    'dqdv',
    'gitt',
    'plotutils',
    'utils',
]
