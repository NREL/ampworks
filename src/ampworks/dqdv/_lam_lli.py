from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if TYPE_CHECKING:  # pragma: no cover
    from ._tables import AgingTable, DqdvFitTable


def calc_lam_lli(fit_result: DqdvFitTable) -> pd.DataFrame:
    r"""
    Calculate aging parameters.

    Uses full cell capacity and fitted x0/x1 values from dqdv/dvdq fits to
    calculate theoretical electrode capacities, loss of active material (LAM),
    and loss of lithium inventory (LLI).

    Electrode capacities (Q) and losses of active material (LAM) are

    .. math::

        Q_{ed} = \frac{\rm capacity}{x_{1,ed} - x_{0,ed}}, \quad \quad
        {\rm LAM}_{ed} = 1 - \frac{Q_{ed}}{Q_{ed}[0]},

    where :math:`ed` is generic for 'electrode'. Output uses 'n' and 'p' to
    differentiate between negative and positive electrodes, respectively. Loss
    of lithium inventory (LLI) is

    .. math::

        {\rm Inv} = x_{1,n}Q_{n} + x_{1,p}Q_{p}, \quad \quad
        {\rm LLI} = 1 - \frac{\rm Inv}{\rm Inv[0]},

    where :math:`{\rm Inv}` is the total lithium inventories using capacities
    :math:`Q` from above. If standard deviations of the x0/x1 stoichiometries
    are available in ``results`` (and are not NaN), then they are propagated
    to give uncertainty estimates for the LAM/LLI values. Reported uncertainties
    come from first-order Taylor series assumptions. If you trust your x0/x1
    fits but see large or inconsistent uncertainties then it is also safe to
    trust the LAM/LLI values, but you may want to neglect LAM/LLI uncertainties.

    Parameters
    ----------
    fit_result : DqdvFitResult
        Results containing the fitted x0/x1 values from dqdv/dvdq fits.

    Returns
    -------
    aging_result : AgingResult
        Electrode capacities (Q) and loss of active material (LAM) for the
        negative (n) and positive (p) electrodes, and loss of lithium inventory
        (LLI). Capacities are in Ah. All other outputs are unitless.

    """

    from ._tables import AgingTable

    df = fit_result.df.copy()

    Ah = df.Ah.to_numpy()

    xn0, xn0_std = df.xn0.to_numpy(), df.xn0_std.to_numpy()
    xn1, xn1_std = df.xn1.to_numpy(), df.xn1_std.to_numpy()
    xp0, xp0_std = df.xp0.to_numpy(), df.xp0_std.to_numpy()
    xp1, xp1_std = df.xp1.to_numpy(), df.xp1_std.to_numpy()

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

    aging = pd.DataFrame({
        'Qn': Qn, 'Qn_std': Qn_std,
        'Qp': Qp, 'Qp_std': Qp_std,
        'LAMn': LAMn, 'LAMn_std': LAMn_std,
        'LAMp': LAMp, 'LAMp_std': LAMp_std,
        'LLI': LLI, 'LLI_std': LLI_std,
    })

    return AgingTable(aging)


def plot_lam_lli(aging_table: AgingTable, fit_table: DqdvFitTable,
                 x_col: str | None = None, std: bool = True) -> None:

    from ampworks.plotutils import format_ticks

    df = pd.concat([aging_table.df, fit_table.df], axis=1)

    if x_col is None:
        xplt, xlabel = df.index, 'Index'
    else:
        xplt, xlabel = df[x_col], x_col.capitalize()

    shaded = {'alpha': 0.2, 'color': 'C0'}

    _, axs = plt.subplots(
        2, 3, figsize=[9.0, 3.5], sharex=True, constrained_layout=True,
    )

    df.plot(
        x_col, ['Qn', 'Qp', 'Ah', 'LAMn', 'LAMp', 'LLI'], subplots=True,
        color='C0', legend=False, xlabel=xlabel, ax=axs.flatten(),
    )

    # first row: Qn, Qp, Q
    if std:
        Qn, Qn_std = df[['Qn', 'Qn_std']].T.to_numpy()
        axs[0, 0].fill_between(xplt, Qn - Qn_std, Qn + Qn_std, **shaded)

        Qp, Qp_std = df[['Qp', 'Qp_std']].T.to_numpy()
        axs[0, 1].fill_between(xplt, Qp - Qp_std, Qp + Qp_std, **shaded)

    axs[0, 0].set_ylabel(r'$Q_{\rm NE}$ [Ah]')
    axs[0, 1].set_ylabel(r'$Q_{\rm PE}$ [Ah]')
    axs[0, 2].set_ylabel(r'$Q_{\rm cell}$ [Ah]')

    # second row: LAMn, LAMp, LLI
    if std:
        LAM, LAM_std = df[['LAMn', 'LAMn_std']].T.to_numpy()
        axs[1, 0].fill_between(xplt, LAM - LAM_std, LAM + LAM_std, **shaded)

        LAM, LAM_std = df[['LAMp', 'LAMp_std']].T.to_numpy()
        axs[1, 1].fill_between(xplt, LAM - LAM_std, LAM + LAM_std, **shaded)

        LLI, LLI_std = df[['LLI', 'LLI_std']].T.to_numpy()
        axs[1, 2].fill_between(xplt, LLI - LLI_std, LLI + LLI_std, **shaded)

    axs[1, 0].set_ylabel(r'LAM$_{\rm NE}$ [$-$]')
    axs[1, 1].set_ylabel(r'LAM$_{\rm PE}$ [$-$]')
    axs[1, 2].set_ylabel(r'LLI [$-$]')

    # formatting
    format_ticks(axs, xdiv=2, ydiv=2)
