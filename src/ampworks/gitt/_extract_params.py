from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from scipy.stats import linregress
from scipy.integrate import trapezoid

if TYPE_CHECKING:  # pragma: no cover
    from ._dataclasses import CellDescription, GITTDataset


def extract_params(sign: int, cell: CellDescription, data: GITTDataset,
                   ref: int = 1) -> pd.DataFrame:
    """_summary_

    Parameters
    ----------
    sign : int
        The sign of the current pulses to process. Use `-1` for negative pulses
        (discharging) and `+1` for positive pulses (charging).
    cell : CellDescription
        Description of the cell.
    data : GITTDataset
        The GITT data to process.
    ref : int, optional
        Intercalation fraction reference value. Must be in {0, 1}, enforcing
        that the lower bound is zero or the upper bound is 1 (default).

    Returns
    -------
    params : dict
        A dictionary of the extracted parameters from each pulse. The keys are
        `xs [-]` for the intercalation fractions, `Ds [m2/s]` for diffusivity,
        `i0 [A/m2]` for exchange current density, and `OCV [V]` for the OCV.
    stats : dict
        Only returned when 'return_stats' is True. Provides key/value pairs for
        the number of pulses, average pulse current, and average rest and pulse
        times.

    References
    ----------
    TODO

    """

    # Pull arrays from data
    time = data.time.copy()
    current = data.current.copy()
    voltage = data.voltage.copy()

    # Constants
    R = 8.314e3  # Gas constant [J/kmol/K]
    F = 96485.33e3  # Faraday's constant [C/kmol]

    # Find pulse indexes
    if sign == -1:
        I_pulse = np.mean(current[current < 0.])
    elif sign == +1:
        I_pulse = np.mean(current[current > 0.])
    else:
        raise ValueError("Invalid 'sign' value, must be in {-1, +1}.")

    start, stop = data.find_pulses(sign)

    if start.size != stop.size:
        raise ValueError("Size mismatch: The number of detected pulse"
                         f" starts ({start.size}) and stops ({stop.size})"
                         " do not agree. This typically occurs due to a"
                         " missing rest. You will likely need to manually"
                         " remove affected pulse(s).")

    # OCV
    Eeq = voltage[start]

    # Diffusivity
    xs = np.zeros_like(Eeq)
    for i in range(xs.size):
        delta_capacity = trapezoid(
            x=time[start[i]:stop[i] + 1] / 3600.,
            y=current[start[i]:stop[i] + 1] / cell.mass_AM,
        )

        if i == 0:
            xs[i] = 1.
        else:
            xs[i] = xs[i-1] - delta_capacity / cell.spec_capacity_AM

    if ref == 0:
        xs = xs - xs.min()
    elif ref == 1:
        xs = xs - xs.max() + 1
    else:
        raise ValueError("Invalid 'ref' value, must be in {0, 1}.")

    dEeq_dxs = np.gradient(Eeq, xs)

    dV_droot_t = np.zeros_like(xs)
    shifts = np.zeros(xs.size, dtype=int)
    for i in range(xs.size):

        j1_target = time[start[i]] + 1.
        j2_target = time[start[i]] + 10.
        j_candidates = np.arange(start[i] + 1, time.size)

        j1_rel = np.argmin(np.abs(time[j_candidates] - j1_target))
        j2_rel = np.argmin(np.abs(time[j_candidates] - j2_target))

        shift = j_candidates[j1_rel] - start[i]
        end = j_candidates[j2_rel]

        if end - (start[i] + shift) < 10:
            end += 10

        t_pulse = time[start[i] + shift:end + 1] - time[start[i]]
        V_pulse = voltage[start[i] + shift:end + 1]

        result = linregress(np.sqrt(t_pulse), V_pulse)

        shifts[i] = shift
        dV_droot_t[i] = result.slope

    Ds = 4./np.pi * (I_pulse*cell.molar_vol_AM / (cell.surf_area_AM*F))**2 \
        * (dEeq_dxs/dV_droot_t)**2

    # Exchange current density
    eta_ct = voltage[start + shifts] - voltage[start]
    i0 = (R*data.avg_temperature / F) * (I_pulse / (eta_ct*cell.surf_area_AM))

    # Store outputs
    params = pd.DataFrame({
        'xs [-]': xs,
        'Ds [m2/s]': Ds,
        'i0 [A/m2]': i0,
        'Eeq [V]': Eeq,
    })

    params.sort_values(by='xs [-]', inplace=True, ignore_index=True)

    return params
