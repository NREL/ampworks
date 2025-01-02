from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

import numpy as np

if TYPE_CHECKING:  # pragma: no cover
    import numpy.typing as npt


@dataclass(slots=True)
class CellDescription:
    """
    Cell description wrapper

    Parameters
    ----------
    thick_ed : float
        Electrode thickness [m].
    area_ed : float
        Projected electrode area (e.g., pi*R**2 for coin cells, L*W for pouch
        cells, etc.) [m2].
    eps_el : float
        Electrolyte/pore volume fraction [-].
    eps_CBD : float
        Carbon-binder-domain volume fraction [-]. See notes for more info.
    radius_AM : float
        Active material particle radius [m].
    rho_AM : float
        Active material mass density [kg/m3].
    mass_AM : float
        Total active material mass [kg].
    molar_mass_AM : float
        Active material molar mass [kg/kmol].

    Returns
    -------
    None.

    Notes
    -----
    A "convenient" way to get ``eps_CBD`` requires knowledge of the densities
    and masses for all solid phases in your slurry (carbon additive, binder,
    and active material). The volume fraction for any phase :math:`m` is

    .. math::

        \\varepsilon_{m} = f_{m} \\varepsilon_{\\rm s},

    where :math:`f_{m}` is the volume of phase :math:`m` per volume of solid
    phase and :math:`\\varepsilon_{\\rm s} = 1 - \\varepsilon_{\\rm el}` is
    the total solid-phase volume fraction. :math:`f_{m}` is calculated as

    .. math::

        f_{m} = \\frac{m_{m} / \\rho_{m}}{\\sum_{i=1}^{N} m_{i} / \\rho_{i}},

    Here, the numerator uses the mass and density of phase :math:`m` to get
    its individual volume, and the denominator sums over all :math:`N` solid
    phases to calculate the total solid-phase volume. Using these expressions,
    you can separately calculate volume fractions for the carbon additive and
    binder. Finally, adding their values together gives

    .. math::

        \\varepsilon_{\\rm CBD} = \\varepsilon_{\\rm C}
                                + \\varepsilon_{\\rm B}.

    """

    thick_ed: float
    area_ed: float
    eps_el: float
    eps_CBD: float
    radius_AM: float
    rho_AM: float
    mass_AM: float
    molar_mass_AM: float

    @property
    def volume_ed(self) -> float:
        """Electrode volume [m3]."""
        return self.thick_ed*self.area_ed

    @property
    def spec_capacity_AM(self) -> float:
        """Theoretical specific capacity [Ah/kg]."""
        return 96485.33e3 / (3600.*self.molar_mass_AM)

    @property
    def molar_vol_AM(self) -> float:
        """Active material molar volume [m3/kmol]."""
        return self.molar_mass_AM / self.rho_AM

    @property
    def eps_AM(self) -> float:
        """Active material volume fraction [-]."""
        return 1. - self.eps_el - self.eps_CBD

    @property
    def surf_area_AM(self) -> float:
        """Total active material surface area [m2]."""
        return 3.*self.eps_AM*self.volume_ed / self.radius_AM


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

        self.time = np.asarray(time)
        self.current = np.asarray(current)
        self.voltage = np.asarray(voltage)
        self.avg_temperature = avg_temperature

        if not all(np.diff(self.time) >= 0.):
            raise ValueError("'time' array must be increasing.")

        if invert_current:
            self.current *= -1.
