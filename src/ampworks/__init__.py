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

from ._core import (
    Dataset,
    read_csv,
    read_excel,
    read_table,
)

__version__ = '0.0.2.dev0'

__all__ = [
    'Dataset',
    'read_csv',
    'read_excel',
    'read_table',
    'ici',
    'gitt',
    'dqdv',
    'utils',
    'datasets',
    'mathutils',
    'plotutils',
    '_in_interactive',
    '_in_notebook',
]


# Lazily load submodules/subpackages
_lazy_modules = {
    'ici': 'ampworks.ici',
    'gitt': 'ampworks.gitt',
    'dqdv': 'ampworks.dqdv',
    'utils': 'ampworks.utils',
    'datasets': 'ampworks.datasets',
    'mathutils': 'ampworks.mathutils',
    'plotutils': 'ampworks.plotutils',
}


def __getattr__(name):
    if name in _lazy_modules:
        module = __import__(_lazy_modules[name], fromlist=[name])
        globals()[name] = module  # cache for later
        return module
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    return list(globals().keys() | __all__)


# Check for interactive and notebook environments
def _in_interactive() -> bool:
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except Exception:
        return False


def _in_notebook() -> bool:
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        return shell in ('ZMQInteractiveShell',)  # Jupyter Notebook or Lab
    except Exception:
        return False
