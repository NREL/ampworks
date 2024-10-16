from numpy import ndarray as _ndarray
from scipy.interpolate import Akima1DInterpolator as _akima


def dydx(x: _ndarray, y: _ndarray, **kwargs) -> _ndarray:
    """
    Calculate numerical derivative dy/dx.

    Parameters
    ----------
    x : 1D array
        Independent variable.
    y : 1D array
        Dependent variable.
    **kwargs : dict, optional
        Keyword arguments. Optional key/value pairs and defaults given below.

        ================= =============================================
        Key               Value (*type*, default)
        ================= =============================================
        smoothing_win_x   smoothing window for x data (*float*, None)
        smoothing_win_y   smoothing window for y data (*float*, None)
        lead_value        leading derivative value (*float*, None)
        ================= =============================================

    Returns
    -------
    dy_dx : ndarray
        First-order numerical derivative dy/dx.

    """

    import numpy as np
    import scipy.signal as sig

    sw_x = kwargs.get('smoothing_win_x', None)
    sw_y = kwargs.get('smoothing_win_y', None)
    lead_value = kwargs.get('lead_value', None)

    if sw_x is not None:
        x = sig.savgol_filter(x, sw_x, 2)

    if sw_y is not None:
        y = sig.savgol_filter(y, sw_y, 2)

    dy_dx = np.diff(y) / np.diff(x)
    if lead_value is not None:
        dy_dx = np.hstack([lead_value, dy_dx])

    return dy_dx


def combinations(values: list[_ndarray], names: list[str] = []) -> list[dict]:
    """
    Generate all value combinations.

    Parameters
    ----------
    values : list[1D array]
        Possible variable values. The array with index ``i`` corresponds to
        the variable ``names[i]``, if provided.
    names : list[str], optional
        Variable names. If not provided, the dictionary will use integers
        from ``0`` to ``len(names) - 1`` as the keys for the output.

    Returns
    -------
    combinations : list[dict]
        Dictionaries for each possible combination of values.

    """

    import itertools

    if names == []:
        names = [i for i in range(len(values))]

    combinations = []
    for combination in itertools.product(*values):
        combinations.append({k: v for k, v in zip(names, combination)})

    return combinations


class makima(_akima):

    def __init__(self, x: _ndarray, y: _ndarray,
                 extrapolate: bool = True) -> None:
        """
        Modified Akima interpolator.

        Parameters
        ----------
        x : 1D array
            Independent variable data.
        y : 1D array
            Dependent variable data.

        """

        super().__init__(x, y)
        self.extrapolate = extrapolate
