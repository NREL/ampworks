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

__version__ = '0.0.1'

__all__ = [
    'dqdv',
    'gitt',
    'plotutils',
    'utils',
]


def __getattr__(attr):

    if attr == 'dqdv':
        import ampworks.dqdv as dqdv
        return dqdv
    elif attr == 'gitt':
        import ampworks.gitt as gitt
        return gitt
    elif attr == 'plotutils':
        import ampworks.plotutils as plotutils
        return plotutils
    elif attr == 'utils':
        import ampworks.utils as utils
        return utils


def __dir__():
    public_symbols = (globals().keys() | __all__)
    return list(public_symbols)
