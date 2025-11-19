from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.integrate import cumulative_trapezoid

if TYPE_CHECKING:  # pragma: no cover
    import ampworks as amp
    

def _detect_pulses(data: amp.Dataset, tmin: float = 0., tmax: float = 20.,
                   plot: bool = False) -> amp.Dataset:
    
    df = data.copy()
    df = df.reset_index(drop=True)
    
    df['Seconds'] -= df['Seconds'].min()
    df['Hours'] = df['Seconds'] / 3600.

    # Create State column
    df['State'] = 'R'
    df.loc[df['Amps'] > 0, 'State'] = 'C'
    df.loc[df['Amps'] < 0, 'State'] = 'D'
    
    # Add Ah and SOC columns
    is_net_charge = df['Volts'].iloc[0] < df['Volts'].iloc[-1]
    sign = +1 if is_net_charge else -1
    
    df['Ah'] = cumulative_trapezoid(sign*df['Amps'], df['Hours'], initial=0.)
    
    if is_net_charge:
        df['SOC'] = df['Ah'] / df['Ah'].max()
    else:    
        df['SOC'] = 1. - df['Ah'] / df['Ah'].max()
    
    # Create 'Step' column to group by State and Step
    state0 = df['State'].iloc[0]
    df['Step'] = (df['State'] != df['State'].shift(fill_value=state0)).cumsum()
    
    groups = df.groupby(['State', 'Step'])
    df['StepTime'] = groups['Seconds'].transform(lambda x: x - x.iloc[0])
    
    # Loop over (State, Step) groups to locate charge/discharge pulses
    df['DisPulse'] = pd.NA
    df['ChgPulse'] = pd.NA

    dis_count = 1
    chg_count = 1
    
    for (state, _), g in groups:
        
        idx = g.index
        if idx[0] != df.index[0]:
            idx = np.hstack([idx[0] - 1, idx], dtype=int)
        
        before, after = idx[0], idx[-1] + 1
        if (state == 'R') or (g['StepTime'].max() > tmax):
            continue
        elif any(df.loc[[before, after], 'State'] != 'R'):
            continue        
        
        if (state == 'D') and (g['StepTime'].max() >= tmin):
            df.loc[idx, 'DisPulse'] = dis_count
            dis_count += 1
        elif (state == 'C') and (g['StepTime'].max() >= tmin):
            df.loc[idx, 'ChgPulse'] = chg_count
            chg_count += 1
            
    # Plot
    if plot:
        _, ax = plt.subplots(figsize=(8, 4))

        ax.plot(df['Hours'], df['Volts'], color='black', lw=1)
        ax.set_xlabel('Hours')
        ax.set_ylabel('Volts')

        for _, g in df.groupby('DisPulse'):

            x0 = g['Hours'].iloc[0]
            x1 = g['Hours'].iloc[-1]

            # shade region
            ax.axvspan(x0, x1, alpha=0.3, color='red')

            # markers on first and last points
            y0 = g['Volts'].iloc[0]
            y1 = g['Volts'].iloc[-1]
            ax.scatter([x0, x1], [y0, y1], color='red', zorder=5)
            
        for _, g in df.groupby('ChgPulse'):

            x0 = g['Hours'].iloc[0]
            x1 = g['Hours'].iloc[-1]

            # shade region
            ax.axvspan(x0, x1, alpha=0.3, color='blue')

            # markers on first and last points
            y0 = g['Volts'].iloc[0]
            y1 = g['Volts'].iloc[-1]
            ax.scatter([x0, x1], [y0, y1], color='blue', zorder=5)
            
        amp.plotutils.format_ticks(ax)
    
    return df    
        
        
def extract_impedance(data: amp.Dataset, tmin: float = 0., tmax: float = 20.,
                      plot: bool = False) -> pd.DataFrame:

    df = _detect_pulses(data, tmin=tmin, tmax=tmax, plot=plot)
            
    results = None
    for (idx, g) in df.groupby('DisPulse', dropna=True):
        
        seconds0 = g['Seconds'].iloc[0]
        seconds1 = g['Seconds'].iloc[-1]
        delta_seconds = seconds1 - seconds0

        volts0 = g['Volts'].iloc[0]
        volts1 = g['Volts'].iloc[-1]
        amps_avg = g.loc[g['Amps'] != 0, 'Amps'].mean()
        
        soc = g['SOC'].iloc[0]
        ohms = np.abs(volts1 - volts0) / np.abs(amps_avg)
        
        row = pd.DataFrame({
            'PulseNum': [idx],
            'State': ['D'],
            'Hours0': [seconds0 / 3600.],
            'DeltaSeconds': [delta_seconds],
            'Volts0': [volts0],
            'Volts1': [volts1],
            'AmpsAvg': [amps_avg],
            'SOC': [soc],
            'Ohms': [ohms],
        })
        
        results = pd.concat([results, row], ignore_index=True)

    for (idx, g) in df.groupby('ChgPulse', dropna=True):
        
        seconds0 = g['Seconds'].iloc[0]
        seconds1 = g['Seconds'].iloc[-1]
        delta_seconds = seconds1 - seconds0

        volts0 = g['Volts'].iloc[0]
        volts1 = g['Volts'].iloc[-1]
        amps_avg = g.loc[g['Amps'] != 0, 'Amps'].mean()
        
        soc = g['SOC'].iloc[0]
        ohms = np.abs(volts1 - volts0) / np.abs(amps_avg)
        
        row = pd.DataFrame({
            'PulseNum': [idx],
            'State': ['C'],
            'Hours0': [seconds0 / 3600.],
            'DeltaSeconds': [delta_seconds],
            'Volts0': [volts0],
            'Volts1': [volts1],
            'AmpsAvg': [amps_avg],
            'SOC': [soc],
            'Ohms': [ohms],
        })
        
        results = pd.concat([results, row], ignore_index=True)
        
    return results
