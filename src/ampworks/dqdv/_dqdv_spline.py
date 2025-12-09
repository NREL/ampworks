from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import matplotlib.pyplot as plt

from scipy.interpolate import make_splrep
from scipy.integrate import cumulative_trapezoid

if TYPE_CHECKING:  # pragma: no cover
    import ampworks as amp
    import numpy.typing as npt


class DqdvSpline:

    def fit(self, data: amp.Dataset, s: float = 0.) -> None:

        data = data.reset_index(drop=True)

        # add Ah and SOC columns
        is_net_charge = data['Volts'].iloc[0] < data['Volts'].iloc[-1]
        sign = +1 if is_net_charge else -1

        if 'Ah' in data.columns and data['Ah'].min() == 0.:
            pass
        else:
            data['Ah'] = cumulative_trapezoid(
                sign*data['Amps'], x=data['Seconds'] / 3600., initial=0.,
            )

        if is_net_charge:
            data['SOC'] = data['Ah'] / data['Ah'].max()
        else:
            data['SOC'] = 1. - data['Ah'] / data['Ah'].max()

        # fit smoothing spline
        _, mask = np.unique(data['SOC'], return_index=True)

        data = data.iloc[mask].reset_index(drop=True)
        data = data.sort_values('SOC', ignore_index=True)

        Ah = data['Ah'].to_numpy()
        SOC = data['SOC'].to_numpy()
        Volts = data['Volts'].to_numpy()

        # set spline and derivative
        self._volts = make_splrep(SOC, Volts, s=s)
        self._dvdq = self._volts.derivative()

        # add fit attributes
        self.Ah_ = Ah
        self.SOC_ = SOC
        self.Volts_ = Volts
        self.score_ = np.sqrt(np.mean((self.volts_(SOC) - Volts)**2))

        return self

    def plot(self) -> plt.Axes:

        from ampworks.plotutils import format_ticks, focused_limits

        volts_dat = self.Volts_
        dvdq_dat = np.gradient(self.Volts_, self.SOC_)
        dqdv_dat = 1. / dvdq_dat

        volts_fit = self.volts_(self.SOC_)
        dvdq_fit = self.dvdq_(self.SOC_)
        dqdv_fit = self.dqdv_(self.SOC_)

        mV_err = (volts_fit - volts_dat)*1e3

        _, axs = plt.subplots(2, 2, figsize=[8, 5], layout='tight')

        axs[0, 0].plot(self.SOC_, volts_dat, '.', color='C0', alpha=0.5)
        axs[0, 0].plot(self.SOC_, volts_fit, '--k')
        axs[0, 0].set_xlabel('SOC [-]')
        axs[0, 0].set_ylabel('Voltage [V]')
        axs[0, 0].legend(['Data', 'Spline'], frameon=False, loc='upper left')

        axs[1, 0].plot(self.SOC_, mV_err, '-k')
        axs[1, 0].set_xlabel('SOC [-]')
        axs[1, 0].set_ylabel('Error [mV]')

        axs[0, 1].plot(volts_dat, dqdv_dat, '.', color='C0', alpha=0.5)
        axs[0, 1].plot(volts_fit, dqdv_fit, '--k')

        ymin, ymax = dqdv_fit.min(), dqdv_fit.max()
        ylim = (ymin - 0.05*(ymax - ymin), ymax + 0.05*(ymax - ymin))
        axs[0, 1].set_ylim(ylim)
        axs[0, 1].set_xlabel('dqdv [1/V]')
        axs[0, 1].set_ylabel('Voltage [V]')

        axs[1, 1].plot(self.SOC_, dvdq_dat, '.', color='C0', alpha=0.5)
        axs[1, 1].plot(self.SOC_, dvdq_fit, '--k')

        ylim = focused_limits(dvdq_fit)
        axs[1, 1].set_ylim(ylim)
        axs[1, 1].set_xlabel('SOC [-]')
        axs[1, 1].set_ylabel('dvdq [V]')

        format_ticks(axs)

    def volts_(self, soc: npt.ArrayLike) -> npt.ArrayLike:
        if not hasattr(self, '_volts'):
            raise RuntimeError("Call 'fit' before evaluating.")
        return self._volts(soc)

    def dvdq_(self, soc: npt.ArrayLike) -> npt.ArrayLike:
        if not hasattr(self, '_dvdq'):
            raise RuntimeError("Call 'fit' before evaluating.")
        return self._dvdq(soc)

    def dqdv_(self, soc: npt.ArrayLike) -> npt.ArrayLike:
        if not hasattr(self, '_dvdq'):
            raise RuntimeError("Call 'fit' before evaluating.")
        return 1. / self._dvdq(soc)
