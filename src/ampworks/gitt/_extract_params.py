from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy.stats import linregress
from scipy.interpolate import Akima1DInterpolator

if TYPE_CHECKING:  # pragma: no cover
    from ._dataclasses import CellDescription, GITTDataset


def extract_params(flag: int, cell: CellDescription, data: GITTDataset,
                   return_stats: bool = False, **options) -> pd.DataFrame:
    """_summary_

    Parameters
    ----------
    flag : int
        _description_
    cell : CellDescription
        _description_
    data : GITTDataset
        _description_
    return_stats : bool, optional
        _description_, by default False

    Returns
    -------
    pd.DataFrame
        _description_

    Raises
    ------
    ValueError
        _description_
        
    """
    
    # Options
    options = options.copy()
    
    R2_lim = options.pop('R2_lim', 0.95)
    replace_nans = options.pop('replace_nans', True)
    
    if len(options):
        invalid_keys = list(options.keys())
        raise ValueError("'options' contains invalid key/value pairs:"
                         f" {invalid_keys=}")
    
    # Pull arrays from data
    time = data.time.copy()
    current = data.current.copy()
    voltage = data.voltage.copy()
    
    # Constants
    R = 8.314e3  # Gas constant [J/kmol/K]
    F = 96485.33e3  # Faraday's constant [C/kmol]
    
    # Find pulse indexes
    if flag == 1:
        I_pulse = np.mean(current[current > 0.])
        I_tmp = np.where(current > 0.5*I_pulse, 1, 0)
    elif flag == -1:
        I_pulse = np.mean(current[current < 0.])
        I_tmp = np.where(current < 0.5*I_pulse, 1, 0)
        
    idx1 = np.where(np.diff(I_tmp) > 0.9)[0]
    idx2 = np.where(I_tmp > -0.9)[0]
    start = np.intersect1d(idx1, idx2)
    
    idx1 = np.where(I_tmp > 0.9)[0]
    idx2 = np.where(np.diff(I_tmp) < -0.9)
    stop = np.intersect1d(idx1, idx2)
    
    if start.size != stop.size:
        idxmin = min(start.size, stop.size)
        start = start[:idxmin]
        stop = stop[:idxmin]
    
    # Extract OCV
    OCV = voltage[start]
    
    # Extract diffusivity
    xs = np.zeros_like(OCV)
    xs[0] = 1.
    
    for i in range(xs.size - 1):
        delta_capacity = np.trapezoid(
            x=time[start[i]:stop[i] + 1] / 3600.,
            y=current[start[i]:stop[i] + 1] / cell.mass_AM,
        )
        
        xs[i+1] = xs[i] - delta_capacity / cell.capacity
        
    dOCV_dxs = np.gradient(OCV) / np.gradient(xs)
    
    shifts = np.zeros(xs.size, dtype=int)
    dV_droot_t = np.zeros_like(xs)
    for i in range(dV_droot_t.size):
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
    
    Ds = 4./np.pi * (I_pulse*cell.Vm_AM / (cell.As_AM*F))**2 \
       * (dOCV_dxs/dV_droot_t)**2
       
    if any(np.isnan(Ds)) and replace_nans:
        nan = np.isnan(Ds)
        
        if xs[0] > xs[-1]:    
            x, y = np.flip(xs[~nan]), np.flip(Ds[~nan])
        else:
            x, y = xs[~nan], Ds[~nan]
            
        interpolator = Akima1DInterpolator(x, y, method='makima')
            
        Ds[nan] = interpolator(xs[nan])
       
    # Extract exchange current density    
    eta_ct = voltage[start+shifts] - voltage[start]
    i0 = (R*data.avg_temperature / F) * (I_pulse / (eta_ct*cell.As_AM))
    
    # Store output(s)
    df = pd.DataFrame({
        'xs': xs,
        'Ds': Ds,
        'i0': i0,
        'OCV': OCV,
    })
    
    stats = {
        'n_pulses': start.size,
        'I_pulse [A]': I_pulse,
        'i_pulse [A/m2]': I_pulse / cell.area,
        't_pulse [s]': np.mean(time[stop] - time[start]),
        't_rest [s]': np.mean(time[start[1:]] - time[stop[:-1]]),
    }
    
    if return_stats:
        return df, stats
    else:
        return df    