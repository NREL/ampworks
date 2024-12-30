from numpy import ndarray as _ndarray


def reset_rcparams() -> None:
    """
    Sets ``plt.rcParams`` back to defaults.

    Returns
    -------
    None.

    """

    import matplotlib.pyplot as plt

    plt.rcdefaults()


def set_tick_rcparams(allsides: bool = True, minorticks: bool = True,
                      direction: str = 'in') -> None:
    """
    Sets ``plt.rcParams`` tick details.

    Parameters
    ----------
    allsides : bool, optional
        Turns on ticks for top and right sides. The default is True.
    minorticks : bool, optional
        Makes minor ticks visible. The default is True.
    direction : str, optional
        Tick direction from {'in', 'out'}. The default is 'in'.

    Returns
    -------
    None.

    """

    import matplotlib.pyplot as plt

    if allsides:
        plt.rcParams['xtick.top'] = True
        plt.rcParams['ytick.right'] = True

    if minorticks:
        plt.rcParams['xtick.minor.visible'] = True
        plt.rcParams['ytick.minor.visible'] = True

    if direction not in ['in', 'out']:
        raise ValueError(f"{direction=} is not a valid value; supported"
                         + " values are {'in', 'out'}.")
    else:
        plt.rcParams['xtick.direction'] = direction
        plt.rcParams['ytick.direction'] = direction


def set_font_rcparams(fontsize: int = 10, family: str = 'sans-serif') -> None:
    """
    Sets ``plt.rcParams`` font details.

    Parameters
    ----------
    fontsize : int, optional
        Font size to use across all figures. The default is 10.
    family : str, optional
        Font family from {'serif', 'sans-serif'}. The default is 'sans-serif'.

    Returns
    -------
    None.

    """

    import matplotlib.pyplot as plt

    plt.rcParams['font.size'] = fontsize

    if family == 'serif':
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['mathtext.fontset'] = 'dejavuserif'
    elif family == 'sans-serif':
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['mathtext.fontset'] = 'dejavusans'
    else:
        raise ValueError(f"{family=} is not a valid value; supported"
                         + " values are {'serif', 'sans-serif'}.")


def format_ticks(ax: object, xdiv: int = None, ydiv: int = None) -> None:
    """
    Formats ``ax`` ticks.

    Top and right ticks are turned on, tick direction is set to 'in', and
    minor ticks are made visible with the specified number of subdivisions.

    Parameters
    ----------
    ax : object
        An ``axis`` instance from a ``matplotlib`` figure.
    xdiv : int, optional
        Number of divisions between x major ticks. The default is None, which
        performs an 'auto' subdivision.
    ydiv : int, optional
        Number of divisions between y major ticks. The default is None, which
        performs an 'auto' subdivision.

    Returns
    -------
    None.

    """

    import matplotlib as mpl

    if ax.get_xaxis().get_scale() != 'log':
        ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(xdiv))

    if ax.get_yaxis().get_scale() != 'log':
        ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(ydiv))

    ax.tick_params(axis='x', top=True, which='both', direction='in')
    ax.tick_params(axis='y', right=True, which='both', direction='in')


def add_text(ax: object, xloc: float, yloc: float, text: str) -> None:
    """
    Adds text to ``ax`` at a specified location.

    Parameters
    ----------
    ax : object
        An ``axis`` instance from a ``matplotlib`` figure.
    xloc : float
        Relative location (0-1) for text start in x-direction.
    yloc : float
        Relative location (0-1) for text start in y-direction.
    text : str
        Text string to add to figure.

    Returns
    -------
    None.

    """

    ax.text(xloc, yloc, text, transform=ax.transAxes)


def cb_line_plot(ax: object, xdata: list[_ndarray], ydata: list[_ndarray],
                 zdata: _ndarray, cmap: str = 'jet', **kwargs) -> None:

    import numpy as np
    import matplotlib as mpl

    cmap = mpl.colormaps[cmap]

    cbtype = kwargs.pop('cbtype', 'continuous')
    if cbtype == 'continuous':
        zmin = kwargs.pop('zmin', zdata.min())
        zmax = kwargs.pop('zmax', zdata.max())

        norm = mpl.colors.Normalize(vmin=zmin, vmax=zmax)

        cbticks = kwargs.pop('cbticks', None)
        cbticklabels = kwargs.pop('cbticklabels', None)

    elif cbtype == 'discrete':
        zmin = kwargs.pop('zmin', 0)
        zmax = kwargs.pop('zmax', zdata.size + 1)

        norm = mpl.colors.BoundaryNorm(np.arange(zmin, zmax, 1), cmap.N)

        cbticks = kwargs.pop('cbticks', np.arange(zmin + 0.5, zmax + 0.5, 1))
        cbticklabels = kwargs.pop('cbticklabels', zdata)

    else:
        raise ValueError(f"{cbtype=} is not a valid value; supported"
                         + " values are {'continuous', 'discrete'}.")

    sm = mpl.pyplot.cm.ScalarMappable(cmap=cmap, norm=norm)
    if cbtype == 'continuous':
        colors = [sm.to_rgba(z) for z in zdata]
    elif cbtype == 'discrete':
        colors = [sm.to_rgba(z) for z in range(zdata.size + 1)]

    ls = kwargs.pop('linestyle', '-')
    for x, y, color in zip(xdata, ydata, colors):
        ax.plot(x, y, linestyle=ls, color=color)

    cax = kwargs.pop('cax', ax)
    if cax is not None:
        cb = mpl.pyplot.colorbar(sm, ax=cax, ticks=cbticks)

        if cbticklabels is not None:
            cb.set_ticklabels(cbticklabels)

        if cbtype == 'discrete':
            cb.minorticks_off()

        cblabel = kwargs.pop('cblabel', None)
        if cblabel is not None:
            cb.set_label(cblabel)

    if kwargs.pop('format_ticks', True):
        format_ticks(ax, xdiv=kwargs.get('xdiv', None),
                     ydiv=kwargs.get('ydiv', None))

    if len(kwargs) != 0:
        ax.set(**kwargs)
