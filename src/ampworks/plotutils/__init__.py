"""
A module designed to enhance plotting with the matplotlib library. Functions
and classes include routines to simplify color scheme management, formatting
axis ticks, fonts, and more, making it easier to create polished and consistent
visualizations.

"""

from ._colors import ColorMap
from ._ticks import minor_ticks, tick_direction, format_ticks

__all__ = [
    'ColorMap',
    'minor_ticks',
    'tick_direction',
    'format_ticks',
]
