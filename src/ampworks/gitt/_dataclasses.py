from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

import numpy as np

if TYPE_CHECKING:  # pragma: no cover
    import numpy.typing as npt

@dataclass(slots=True, eq=False)
class CellDescription:
    """
    Cell description wrapper
    
    Parameters
    ----------
    thick : float
        Electrode thickness [m].
    area : float
        Cell area (e.g., pi*R**2 for coin cells) [m2].
    eps_el : float
        Electrolyte/pore volume fraction [-].
    eps_CBD : float
        Carbon-binder-domain volume fraction [-]. See notes for more info.
    Rp_AM : float
        Active material particle radius [m].
    rho_AM : float
        Active material mass density [kg/m3].
    mass_AM : float
        Total active material mass [kg].
    MW_AM : float
        Active material molecular weight [kg/kmol].
    
    Returns
    -------
    None.
    
    Notes
    -----
    
    """
    
    thick: float
    area: float
    eps_el: float
    eps_CBD: float
    Rp_AM: float
    rho_AM: float
    mass_AM: float
    MW_AM: float
        
    @property
    def volume(self) -> float:
        """Electrode volume [m3]."""
        return self.thick*self.area
    
    @property
    def capacity(self) -> float:
        """Electrode volume [m3]."""
        return 96485.33e3 / (3600.*self.MW_AM)
    
    @property
    def Vm_AM(self) -> float:
        """Electrode volume [m3]."""
        return self.MW_AM / self.rho_AM
    
    @property
    def eps_AM(self) -> float:
        """Active material volume fraction [-]."""
        return 1. - self.eps_el - self.eps_CBD
    
    @property
    def As_AM(self) -> float:
        """Total active material surface area [m2]."""
        return 3.*self.eps_AM*self.volume / self.Rp_AM
    
    
class GITTDataset:
    """GITT dataclass wrapper"""
    
    def __init__(self, time: npt.ArrayLike, current: npt.ArrayLike,
                 voltage: npt.ArrayLike, avg_temperature: float,
                 invert_current: bool = False) -> None:
        """

        Parameters
        ----------
        time : ArrayLike, shape(n,)
            Recorded test times [s].
        current : ArrayLike, shape(n,)
            Timeseries current data [A].
        voltage : ArrayLike, shape(n,)
            Timeseries voltage data [V].
        avg_temperature : float
            Average temperature of the experiment [K].
        invert_current : bool, optional
            Inverts signs for 'current' values. Charge/discharge currents
            should be positive/negative, respectively. The default is False.
            
        Returns
        -------
        None.

        Raises
        ------
        ValueError
            'time' array must be increasing.
            
        """
        
        time = np.asarray(time)
        current = np.asarray(current)
        voltage = np.asarray(voltage)
        
        if not all(np.diff(time) >= 0.):
            raise ValueError("'time' array must be increasing.")
        
        if invert_current:
            current = -1.*current
        
        self.time = time
        self.current = current
        self.voltage = voltage
        self.avg_temperature = avg_temperature
