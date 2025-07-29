from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from scipy.stats import linregress

if TYPE_CHECKING:  # pragma: no cover
    from ._dataclasses import ICIDataset


def extract_params(data: ICIDataset, radius: float, tmin: float = 1,
                   tmax: float = 10) -> dict:
    """Extracts parameters from ICI data
    
    ICI or incrememtal current interuption is an experiment that interupts a
    low-rate charge or discharge experiment with short rests. These experiments
    can be used to extract important parameters for physics-based models. For
    example, a pseudo open-circuit voltage and the solid-phase diffusivity.

    Parameters
    ----------
    data : Dataset
        The sliced ICI data to process. The data must start and end with a rest
        to correctly autodetect switches between zero and non-zero current. 
    radius : float
        The representative particle radius of your active material. It is common
        to use a radius from D50, i.e., the median diameter of a distribution.
    tmin : float, optional
        The minimum relative time (in seconds) within a rest to use when fitting
        diffusivity curves. Defaults to 1. 
    tmax : float, optional
        The maximum relative time (in seconds) within a rest to use when fitting
        diffusivity curves. Defaults to 10. 

    Returns
    -------
    params : dict

    Raises
    ------
    ValueError
        'options' contains invalid key/value pairs.
        
    Notes
    -----
    Rest periods within the dataset are expected to have a current exactly equal
    to zero. You can use data.loc[data['Amps'].abs() <= tol, 'Amps'] = 0 if you
    need to manually zero out currents below some tolerance. This must be done
    before passing in the dataset to this function.
    
    The input values of `tmin` and `tmax` assume that rests occur for at least
    10 seconds. If your protocol uses shorter rests you should adjust these
    accordingly.
    
    References
    ----------

    """

    df = data.copy()
    
    # States based on current direction: charge, discharge, or rests
    df['State'] = 'R'
    df.loc[df['Amps'] > 0, 'State'] = 'C'
    df.loc[df['Amps'] < 0, 'State'] = 'D'
        
    # Counter each time a rest/charge or rest/discharge changeover occurs
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
    for r, g in groups:
        
        if r > 0:
            g = g[
                (g['State'] == 'R') &
                (g['Step.t'] >= tmin) &
                (g['Step.t'] <= tmax)
            ]

            x = np.sqrt(g['Step.t'])
            y = g['Volts']
            
            result = linregress(x, y)
            new_row = pd.DataFrame({
                'Rest': [r],
                'Eeq': [result.intercept],
                'Eeq_err': [result.intercept_stderr],
                'dUdrt': [result.slope],
                'dUdrt_err': [result.stderr],
            })
            
            regression = pd.concat([regression, new_row], ignore_index=True)
                    
    out = pd.merge(summary, regression, on='Rest')
    
    out['dEdt'] = np.gradient(out['Volts'], out['Seconds'])
    out['Ds'] = 4./9./np.pi * (radius * out['dEdt']/out['dUdrt'])**2
    
    return out
