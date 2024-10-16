"""
AmpWorks
========
A tool kit for battery data analysis. Subpackages include the following
capabilities:

    1.) Differential capacity analysis

"""

from . import dqdv
from . import plotutils
from . import utils

__all__ = ['dqdv', 'plotutils', 'utils']

__version__ = '0.0.1'
