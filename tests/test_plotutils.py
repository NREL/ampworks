import pytest
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.ticker import AutoMinorLocator

from ampworks import plotutils as aplt


# tests for _colors submodule
def test_cmap_init():

    cm = aplt.ColorMap('viridis', (0, 1))

    assert cm._vmin == 0
    assert cm._vmax == 1
    assert hasattr(cm, '_sm')

    with pytest.raises(ValueError):
        aplt.ColorMap('viridis', (0,))  # norm must be length 2

    with pytest.raises(ValueError):
        aplt.ColorMap('viridis', (1, 0))  # vmin must be < vmax


def test_cmap_get_color():

    cm = aplt.ColorMap('viridis', (0, 1))

    color = cm.get_color(0.5)

    assert isinstance(color, tuple)
    assert len(color) == 4  # RGBA

    cm = aplt.ColorMap('viridis', (0, 1))
    with pytest.raises(ValueError):
        cm.get_color(1.5)


def test_cmap_colors_from_size():

    size = 5
    colors = aplt.ColorMap.colors_from_size(size, 'viridis')

    assert isinstance(colors, list)
    assert len(colors) == size
    assert all(len(c) == 4 for c in colors)


def test_cmap_colors_from_data():

    data = np.array([[0, 0.5], [0.8, 1]])
    colors = aplt.ColorMap.colors_from_data(data, 'viridis')

    assert isinstance(colors, np.ndarray)
    assert colors.shape == data.shape

    for row in colors:
        for c in row:
            assert len(c) == 4


# tests for _text submodule
def test_add_text():

    # basic
    fig, ax = plt.subplots()

    aplt.add_text(ax, 0.1, 0.1, 'First')
    aplt.add_text(ax, 0.9, 0.9, 'Second')

    texts = [t.get_text() for t in ax.texts]

    assert 'First' in texts
    assert 'Second' in texts
    assert len(ax.texts) == 2

    plt.close(fig)

    # alignment
    fig, ax = plt.subplots()

    aplt.add_text(ax, 0.3, 0.7, 'Aligned', ha='left', va='top')

    text = ax.texts[0]

    assert text.get_ha() == 'left'
    assert text.get_va() == 'top'

    plt.close(fig)


# tests for _ticks submodule
def test_minor_ticks():

    # defaults
    fig, ax = plt.subplots()
    aplt.minor_ticks(ax)

    assert isinstance(ax.xaxis.get_minor_locator(), AutoMinorLocator)
    assert isinstance(ax.yaxis.get_minor_locator(), AutoMinorLocator)

    plt.close(fig)

    # custom
    fig, ax = plt.subplots()
    aplt.minor_ticks(ax, xdiv=4, ydiv=3)

    xloc = ax.xaxis.get_minor_locator()
    yloc = ax.yaxis.get_minor_locator()

    assert isinstance(xloc, AutoMinorLocator) and xloc.ndivs == 4
    assert isinstance(yloc, AutoMinorLocator) and yloc.ndivs == 3

    plt.close(fig)


def test_tick_direction():

    # defaults
    fig, ax = plt.subplots()
    aplt.tick_direction(ax)

    xdir = ax.xaxis.get_tick_params()['direction']
    ydir = ax.yaxis.get_tick_params()['direction']

    assert xdir == 'in'
    assert ydir == 'in'

    plt.close(fig)

    # custom
    fig, ax = plt.subplots()
    aplt.tick_direction(ax, xdir='out', ydir='inout', top=False, right=False)

    xparams = ax.xaxis.get_tick_params()
    yparams = ax.yaxis.get_tick_params()

    assert xparams['direction'] == 'out' and not xparams['top']
    assert yparams['direction'] == 'inout' and not yparams['right']

    plt.close(fig)


def test_format_ticks():

    fig, ax = plt.subplots()
    aplt.format_ticks(
        ax, xdiv=4, ydiv=3, xdir='out', ydir='inout', top=False, right=False,
    )

    xloc = ax.xaxis.get_minor_locator()
    yloc = ax.yaxis.get_minor_locator()

    xparams = ax.xaxis.get_tick_params()
    yparams = ax.yaxis.get_tick_params()

    assert isinstance(xloc, AutoMinorLocator) and xloc.ndivs == 4
    assert isinstance(yloc, AutoMinorLocator) and yloc.ndivs == 3

    assert xparams['direction'] == 'out' and not xparams['top']
    assert yparams['direction'] == 'inout' and not yparams['right']

    plt.close(fig)
