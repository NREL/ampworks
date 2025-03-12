from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy.stats import linregress
from scipy.integrate import trapezoid
from scipy.interpolate import Akima1DInterpolator

if TYPE_CHECKING:  # pragma: no cover
    from ._dataclasses import CellDescription, GITTDataset


def extract_params(pulse_sign: int, cell: CellDescription, data: GITTDataset,
                   return_stats: bool = False, **options) -> dict:
    """_summary_

    Parameters
    ----------
    pulse_sign : int
        The sign of the current pulses to process. Use `+1` for positive pulses
        and `-1` for negative pulses.
    cell : CellDescription
        Description of the cell.
    data : GITTDataset
        The GITT data to process.
    return_stats : bool, optional
        Adds a second return value with some statistics from the experiment,
        see below. The default is False.
    **options : dict, optional
        Keyword options to further control the function behavior. A full list
        of names, types, descriptions, and defaults is given below.
    xs_ref : float, optional
        Shifts the intercalation fraction output value such that the lower or
        upper bound (set via `ref_location`) is `xs_ref`. The default is 1.
    ref_location : {'lower', 'upper'}, optional
        Specifies whether the `xs_ref` value is used as a lower or upper bound.
        The default is 'upper'.
    R2_lim : float, optional
        Lower limit for the coefficient of determination. Pulses whose linear
        regression for `sqrt(time)` vs `voltage` that are less than this value
        result in a diffusivity of `nan`. The default is 0.95.
    replace_nans : bool, optional
        If True (default) this uses interpolation to replace `nan` diffusivity
        values. When False, `nan` values will persist into the output.

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

    Raises
    ------
    ValueError
        'options' contains invalid key/value pairs.

    """

    # Options
    options = options.copy()

    R2_lim = options.pop('R2_lim', 0.95)
    replace_nans = options.pop('replace_nans', True)
    xs_ref = options.pop('xs_ref', 1.)
    ref_location = options.pop('ref_location', 'upper')

    if len(options):
        invalid_keys = list(options.keys())
        raise ValueError("'options' contains invalid key/value pairs:"
                         f" {invalid_keys=}")

    if ref_location not in ['lower', 'upper']:
        raise ValueError(f"Invalid {ref_location=}, must be 'lower', 'upper'.")

    # Pull arrays from data
    time = data.time.copy()
    current = data.current.copy()
    voltage = data.voltage.copy()

    # Constants
    R = 8.314e3  # Gas constant [J/kmol/K]
    F = 96485.33e3  # Faraday's constant [C/kmol]

    # Find pulse indexes
    if pulse_sign == 1:
        I_pulse = np.mean(current[current > 0.])
    elif pulse_sign == -1:
        I_pulse = np.mean(current[current < 0.])

    start, stop = data.find_pulses(pulse_sign)

    if start.size != stop.size:
        raise ValueError("Size mismatch: The number of detected pulse"
                         f" starts ({start.size}) and stops ({stop.size})"
                         " do not agree. This typically occurs due to a"
                         " missing rest. You will likely need to manually"
                         " remove affected pulse(s).")

    # Extract OCV
    OCV = voltage[start]

    # Extract diffusivity
    xs = np.zeros_like(OCV)
    for i in range(xs.size):
        delta_capacity = trapezoid(
            x=time[start[i]:stop[i] + 1] / 3600.,
            y=current[start[i]:stop[i] + 1] / cell.mass_AM,
        )

        if i == 0:
            xs[i] = 1.
        else:
            xs[i] = xs[i-1] - delta_capacity / cell.spec_capacity_AM

    if ref_location == 'lower':
        xs = xs - xs.min() + xs_ref
    elif ref_location == 'upper':
        xs = xs - xs.max() + xs_ref

    dOCV_dxs = np.gradient(OCV) / np.gradient(xs)

    dV_droot_t = np.zeros_like(xs)
    shifts = np.zeros(xs.size, dtype=int)
    for i in range(xs.size):
        shift = np.ceil(0.25*(stop[i] - start[i] + 1)).astype(int)

        t_pulse = time[start[i] + shift:stop[i] + 1] - time[start[i]]
        V_pulse = voltage[start[i] + shift:stop[i] + 1]

        root_t = np.sqrt(t_pulse)

        result = linregress(root_t, V_pulse)
        slope = result.slope

        while abs(result.rvalue**2) < R2_lim:
            if shift + 1 <= np.floor(0.5*(stop[i] - start[i] + 1)):
                shift += 1

                t_pulse = time[start[i] + shift:stop[i] + 1] - time[start[i]]
                V_pulse = voltage[start[i] + shift:stop[i] + 1]

                root_t = np.sqrt(t_pulse)

                result = linregress(root_t, V_pulse)
                slope = result.slope
            else:
                slope = np.nan
                break

        shifts[i] = shift
        dV_droot_t[i] = slope

    Ds = 4./np.pi * (I_pulse*cell.molar_vol_AM / (cell.surf_area_AM*F))**2 \
        * (dOCV_dxs/dV_droot_t)**2

    if any(np.isnan(Ds)) and replace_nans:
        nan = np.isnan(Ds)

        if xs[0] > xs[-1]:
            x, y = np.flip(xs[~nan]), np.flip(Ds[~nan])
        else:
            x, y = xs[~nan], Ds[~nan]

        interpolator = Akima1DInterpolator(
            x, y, method='makima', extrapolate=True,
        )

        Ds[nan] = interpolator(xs[nan])

    # Extract exchange current density
    eta_ct = voltage[start + shifts] - voltage[start]
    i0 = (R*data.avg_temperature / F) * (I_pulse / (eta_ct*cell.surf_area_AM))

    # Store output(s)
    params = pd.DataFrame({
        'xs [-]': xs,
        'Ds [m2/s]': Ds,
        'i0 [A/m2]': i0,
        'OCV [V]': OCV,
    })

    params.sort_values(by='xs [-]', inplace=True, ignore_index=True)

    stats = {
        'num pulses': start.size,
        'avg I_pulse [A]': I_pulse,
        'avg i_pulse [A/m2]': I_pulse / cell.area_ed,
        'avg t_pulse [s]': np.mean(time[stop] - time[start]),
        'avg t_rest [s]': np.mean(time[start[1:]] - time[stop[:-1]]),
    }

    if return_stats:
        return params, stats
    else:
        return params
