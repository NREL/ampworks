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
    'ici',
    'io',
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
    elif attr == 'ici':
        import ampworks.ici as ici
        return ici
    elif attr == 'io':
        import ampworks.io as io
        return io
    elif attr == 'plotutils':
        import ampworks.plotutils as plotutils
        return plotutils
    elif attr == 'utils':
        import ampworks.utils as utils
        return utils


def __dir__():
    public_symbols = (globals().keys() | __all__)
    return list(public_symbols)


def _in_interactive():
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except Exception:
        return False


def _in_notebook():
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        return shell in ('ZMQInteractiveShell',)  # Jupyter Notebook or Lab
    except Exception:
        return False
