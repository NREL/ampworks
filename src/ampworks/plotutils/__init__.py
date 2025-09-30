"""
A module designed to enhance plotting with the matplotlib library. Functions
and classes include routines to simplify color scheme management, formatting
axis ticks, fonts, and more, making it easier to create polished and consistent
visualizations.

"""

from ._colors import ColorMap, colors_from_size, colors_from_data
from ._limits import focused_limits
from ._text import add_text
from ._ticks import minor_ticks, tick_direction, format_ticks

__all__ = [
    'ColorMap',
    'colors_from_size',
    'colors_from_data',
    'focused_limits',
    'add_text',
    'minor_ticks',
    'tick_direction',
    'format_ticks',
]
