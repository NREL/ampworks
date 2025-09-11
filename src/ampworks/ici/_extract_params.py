from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from scipy.stats import linregress
from scipy.integrate import cumulative_trapezoid

if TYPE_CHECKING:  # pragma: no cover
    from ampworks.data import Dataset


def extract_params(data: Dataset, radius: float, tmin: float = 1,
                   tmax: float = 10, return_all: bool = False) -> pd.DataFrame:
    """Extracts parameters from ICI data

    ICI or incrememtal current interruption is an experiment that interrupts a
    low-rate charge or discharge experiment with short rests. These experiments
    can be used to extract important parameters for physics-based models. For
    example, a pseudo open-circuit voltage and the solid-phase diffusivity.

    The following protocol was used to test this algorithm:

        1. Charge (or discharge) at C/10 for 5 min; include a voltage limit.
           Log data every 30 s or every 5 mV change.
        2. If upper or lower cutoff voltage was reached during (1), stop.
        3. Rest for 10 seconds, then repeat step (1). Log data every 0.2 s.

    The protocol assumes any required formation cycles have already been done.
    Details of the implementation are available in [1]_.

    Parameters
    ----------
    data : Dataset
        The sliced ICI data to process. Must have, at a minimum, columns for
        {'Seconds', 'Amps', 'Volts'}. See notes for more information.
    radius : float
        The representative particle radius of your active material (in meters).
        It's common to use D50 / 2, i.e., the median radius of a distribution.
    tmin : float, optional
        The minimum relative rest time (in seconds) to use when fitting the
        voltage vs. sqrt(t) for time constants. Defaults to 1.
    tmax : float, optional
        The maximum relative rest time (in seconds) to use when fitting the
        voltage vs. sqrt(t) for time constants. Defaults to 10.
    return_all : bool, optional
        If False (default), only the extracted parameters vs. state of charge
        are returned. If True, also returns stats with info about each rest.

    Returns
    -------
    params : pd.DataFrame
        Table of parameters. Columns include 'SOC' (state of charge, -), 'Ds'
        (diffusivity, m2/s), and 'Eeq' (equilibrium potential, V).
    stats : pd.DataFrame
        Only returned if `return_all=True`. Provides additional stats about
        each rest, including errors from the voltage vs. sqrt(t) regressions.

    Raises
    ------
    ValueError
        'data' is missing columns, required=['Seconds', 'Amps', 'Volts'].
    ValueError
        'data' should not include both charge and discharge segments.

    Notes
    -----
    Rest periods within the dataset are expected to have a current exactly equal
    to zero. You can use `data.loc[data['Amps'].abs() <= tol, 'Amps'] = 0` if
    you need to manually zero out currents below some tolerance. This must be
    done prior to passing in the dataset to this function.

    This algorithm expects charge/discharge currents to be positive/negaitve,
    respectfully. If your sign convention is opposite this, then the mapping to
    `soc` in the output will be reversed. You should only process data in one
    direction at a time. In other words, if you performed the ICI protocol in
    both the charge and discharge direction you should slice your original data
    into two separate datasets and call this routine twice.

    The input values of `tmin` and `tmax` assume that rests occur for at least
    10 seconds. If your protocol uses shorter rests you should adjust these
    accordingly.

    References
    ----------
    .. [1] Z. Geng, Y. Chien, M. J. Lacey, T. Thiringer, and D. Brandell,
       "Validity of solid-state Li+ diffusion coefficient estimation by
       electrochemical approaches for lithium-ion batteries," EA, 2022,
       DOI: 10.1016/j.electacta.2021.139727

    """

    required = ['Seconds', 'Amps', 'Volts']
    if not any(col in data.columns for col in required):
        raise ValueError(f"'data' is missing columns, {required=}.")

    charging = any(data['Amps'] > 0.)
    discharging = any(data['Amps'] < 0.)

    if charging and discharging:
        raise ValueError(
            "'data' should not include both charge and discharge segments."
        )

    df = data.copy()
    df = df.reset_index(drop=True)

    # Check for pre- and post-rest and pad if not present
    if df['Amps'].iloc[0] != 0.:
        pass  # TODO

    if df['Amps'].iloc[-1] != 0.:
        pass  # TODO

    # States based on current direction: charge, discharge, or rests
    df['State'] = 'R'
    df.loc[df['Amps'] > 0, 'State'] = 'C'
    df.loc[df['Amps'] < 0, 'State'] = 'D'

    # Add in state-of-charge column to map each value to an SOC
    Ah = cumulative_trapezoid(
        df['Amps'].abs(), df['Seconds'] / 3600, initial=0,
    )

    if charging:
        df['SOC'] = Ah / Ah.max()
    elif discharging:
        df['SOC'] = 1 - Ah / Ah.max()

    # Count each time a rest/charge or rest/discharge changeover occurs
    rest = (df['State'] != 'R') & (df['State'].shift(fill_value='R') == 'R')
    df['Rest'] = rest.cumsum()

    # Relative time of each rest/charge or rest/discharge step
    groups = df.groupby(['Rest', 'State'])
    df['Step.t'] = groups['Seconds'].transform(lambda x: x - x.iloc[0])

    # Remove last cycle if not complete, i.e., ended on charge or discharge
    if df.iloc[-1]['State'] != 'R':
        df = df[df['Rest'] != df['Rest'].max()].reset_index(drop=True)

    # Record summary stats for each loop, immediately before the rests
    groups = df[df['State'] != 'R'].groupby('Rest', as_index=False)
    summary = groups.agg(lambda x: x.iloc[-1])

    # Store slope and intercepts (V = m*t^0.5 + b) for each rest
    groups = df.groupby('Rest')

    regression = None
    for idx, g in groups:

        if idx > 0:

            rest = g[g['State'] == 'R']
            pulse = g[g['State'] != 'R']

            dt_rest = rest['Step.t'].max() - rest['Step.t'].min()
            dt_pulse = pulse['Step.t'].max() - pulse['Step.t'].min()

            rest = rest[
                (rest['Step.t'] >= tmin) &
                (rest['Step.t'] <= tmax)
            ]

            x = np.sqrt(rest['Step.t'])
            y = rest['Volts']

            result = linregress(x, y)
            new_row = pd.DataFrame({
                'Rest': [idx],
                'Eeq': [result.intercept],
                'Eeq_err': [result.intercept_stderr],
                'dUdrt': [result.slope],
                'dUdrt_err': [result.stderr],
                'dt_rest': [dt_rest],
                'dt_pulse': [dt_pulse],
            })

            regression = pd.concat([regression, new_row], ignore_index=True)

    stats = pd.merge(summary, regression, on='Rest')
    stats['dEdt'] = np.gradient(stats['Volts'], stats['Seconds'])

    params = pd.DataFrame({
        'SOC': stats['SOC'],
        'Ds': 4./9./np.pi * (radius * stats['dEdt']/stats['dUdrt'])**2,
        'Eeq': stats['Eeq'],
    })

    params.sort_values(by='SOC', inplace=True, ignore_index=True)

    if return_all:
        return params, stats

    return params
