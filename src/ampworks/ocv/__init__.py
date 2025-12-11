"""
Tools for processing and analyzing open-circuit voltage (OCV) behavior. Includes
utilities for estimating OCV curves from low-rate charge/discharge data and
extracting useful features from measured voltage-capacity profiles.

"""

from ._match_peaks import match_peaks

__all__ = [
    'match_peaks',
]
