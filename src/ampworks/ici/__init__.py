"""
Tools to analyze Incremental Current Interruption (ICI) data. Includes functions
to extract diffusion coefficients and equilibrium potentials from experimental
measurements.

"""

from ._extract_params import extract_params

__all__ = [
    'extract_params',
]
