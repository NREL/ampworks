"""
Tools to analyze Hybrid Pulse Power Characterization (HPPC) data. Includes
functions to detect pulses within the protocol and to extract the electrical
impedance from those pulses.

"""

from ._extract_impedance import extract_impedance

__all__ = [
    'extract_impedance',
]
