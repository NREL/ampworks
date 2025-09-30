"""
dQdV
----
Functions for analyzing dQ/dV data from battery experiments. Provides curve
extraction and smoothing, fitting methods, and post-processing of degradation
modes from fitted stoichiometries.

"""

import warnings

import numpy as np
import pandas as pd

from ._dqdv_fitter import DqdvFitter
from ._dqdv_result import DqdvResult

__all__ = [
    'DqdvFitter',
    'DqdvResult',
    'calculate_lam_lli',
    'run_gui',
]


def calculate_lam_lli(results: DqdvResult) -> pd.DataFrame:
    r"""
    Calculate degradation parameters.

    Uses full cell capacity and fitted x0/x1 values from dqdv/dvdq fits to
    calculate theoretical electrode capacities, loss of active material (LAM),
    and loss of lithium inventory (LLI).

    Electrode capacities (Q) and losses of active material (LAM) are

    .. math::

        Q_{ed} = \frac{\rm capacity}{x_{1,ed} - x_{0,ed}}, \quad \quad
        {\rm LAM}_{ed} = 1 - \frac{Q_{ed}}{Q_{ed}[0]},

    where :math:`ed` is used generically for 'electrode'. The output instead
    uses 'n' and 'p' to differentiate between negative and positive electrodes,
    respectively. Loss of lithium inventory (LLI) is

    .. math::

        {\rm Inv} = x_{1,n}Q_{n} + x_{1,p}Q_{p}, \quad \quad
        {\rm LLI} = 1 - \frac{\rm Inv}{\rm Inv[0]},

    where :math:`{\rm Inv}` is the total lithium inventories using capacities
    :math:`Q` above. If standard deviations of the x0/x1 stoichiometries are
    available from the ``results`` (and are not NaN), then they are propagated
    to give uncertainty estmates of the derived values. However, the reported
    uncertainties are estimated via first-order Taylor series can sometimes be
    inaccurate. If you trust your x0/x1 fits but see large or inconsistent
    uncertainties then it is also safe to trust yor LAM/LLI values, but you
    should neglect the uncertainty estimates.

    Parameters
    ----------
    results : DqdvResult
        Results containing the fitted x0/x1 values from dqdv/dvdq fits.

    Returns
    -------
    degradation : pd.DataFrame
        Electrode capacities (Q) and loss of active material (LAM) for the
        negative (n) and positive (p) electrodes, and loss of lithium inventory
        (LLI). Capacities are in Ah. All other outputs are unitless.

    """

    Ah = results.Ah.values

    xn0, xn0_std = results.xn0.values, results.xn0_std.values
    xn1, xn1_std = results.xn1.values, results.xn1_std.values
    xp0, xp0_std = results.xp0.values, results.xp0_std.values
    xp1, xp1_std = results.xp1.values, results.xp1_std.values

    Qn = Ah / (xn1 - xn0)
    Qp = Ah / (xp1 - xp0)

    dQn = Ah / (xn1 - xn0)**2  # ignore lead -1 for xn1 b/c **2 below
    Qn_std = np.sqrt((dQn*xn1_std)**2 + (dQn*xn0_std)**2)

    dQp = Ah / (xp1 - xp0)**2  # ignore lead -1 for xp1 b/c **2 below
    Qp_std = np.sqrt((dQp*xp1_std)**2 + (dQp*xp0_std)**2)

    LAMn = 1. - Qn / Qn[0]
    LAMp = 1. - Qp / Qp[0]

    LAMn_std = Qn_std / Qn[0]
    LAMp_std = Qp_std / Qp[0]

    inv = xn1*Qn + (1. - xp1)*Qp
    LLI = 1. - inv / inv[0]

    inv_std = np.sqrt(
        (xn1*dQn*xn0_std)**2                  # contribution from xn0
        + ((Qn + xn1*dQn)*xn1_std)**2           # contribution from xn1
        + ((1 - xp1)*dQn*xp0_std)**2            # contribution from xp0
        + ((-Qp + (1 - xp1)*dQp)*xn1_std)**2    # contribution from xp1
    )

    LLI_std = inv_std / inv[0]

    degradation = pd.DataFrame({
        'Qn': Qn, 'Qn_std': Qn_std,
        'Qp': Qp, 'Qp_std': Qp_std,
        'LAMn': LAMn, 'LAMn_std': LAMn_std,
        'LAMp': LAMp, 'LAMp_std': LAMp_std,
        'LLI': LLI, 'LLI_std': LLI_std,
    })

    return degradation


def run_gui(jupyter_mode: str = 'external', jupyter_height: int = 650) -> None:
    """
    Run a graphical interface for the Fitter class.

    Parameters
    ----------
    jupyter_mode : {'external', 'inline'}, optional
        How to display the application when running inside a jupyter notebook.
        'external' opens an external web browser (default). 'inline' runs the
        application inside the notebook.
    jupyter_height : int, optional
        Height of the application (in px) when displayed using 'inline'. The
        default is 650.

    Returns
    -------
    None.

    Notes
    -----
    This function is only intended for use inside Jupyter Notebooks. You may
    experience issues if you call it from a normal script, or in an interactive
    session within some IDEs (e.g., Spyder, PyCharm, IPython, etc.). However,
    if you're looking for an alternate way to access the GUI without needing to
    open a Jupyter Notebook, you can use the ``ampworks --app`` command from
    your terminal.

    """

    from ampworks import _in_interactive, _in_notebook

    from .gui_files import _gui

    if not isinstance(jupyter_mode, str):
        raise TypeError("'jupyter_mode' must be type str.")
    elif jupyter_mode not in ['external', 'inline']:
        raise ValueError("'jupyter_mode' must be in {'external', 'inline'}.")

    if not isinstance(jupyter_height, int):
        raise TypeError("'jupyter_height' must be type int.")

    if not _in_notebook():
        jupyter_mode = 'external'

    if _in_interactive() and not _in_notebook():
        warnings.warn(
            "It looks like you're calling `run_gui()` from an interactive"
            " environment (e.g., Spyder, IPython, etc.). If the GUI fails,"
            " try calling the function inside a Jupyter Notebook instead."
            " Or, use the `ampworks --app` command in your terminal."
        )

    _gui.run(jupyter_mode=jupyter_mode, jupyter_height=jupyter_height)
