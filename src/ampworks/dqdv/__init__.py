import warnings

import numpy as np
import pandas as pd
import scipy.optimize as opt
import scipy.interpolate as interp
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt


class Fitter:

    def __init__(self, df_neg: pd.DataFrame = None, df_pos: pd.DataFrame = None,
                 df_cell: pd.DataFrame = None, **kwargs) -> None:
        """
        Wrapper class for differential capacity analysis.

        Parameters
        ----------
        df_neg : pd.DataFrame
            Data for negative electrode OCV.
        df_pos : pd.DataFrame
            Data for positive electrode OCV.
        df_cell : pd.DataFrame
            Data for full cell OCV and derivatives.
        **kwargs : dict, optional
            Keyword arguments. Optional key/value pairs are below:

            ============ ==================================================
            Key          Value (*type*, default)
            ============ ==================================================
            smoothing    smoothing window for fits (*int*, 3)
            figure_font  fontsize for figure elements (*int*, 10)
            bounds       +/- bounds (*list[float]*, [0.1] * 4)
            maxiter      maximum fit iterations (*int*, 1e5)
            xtol         optimization tolerance on x (*float*, 1e-9)
            cost_terms   terms in err func (*list[str]*, ['dqdv', 'dvdq'])
            ============ ==================================================

        Raises
        ------
        ValueError
            Invalid keyword arguments.

        Notes
        -----
        * The df_neg, df_pos, and df_cell dataframes are all required inputs.
          The default ``None`` values allow you to initialize the class first
          and then add each dataframe one at a time. This is primarily so the
          class interfaces well with the data loader in the GUI.
        * Bound indices correspond to x0_neg, x100_neg, x0_pos, and x100_pos.
          Set bounds[i] equal to 1 to use the full interval [0, 1] for x[i].
        * If x[i] +/- bounds[i] exceeds the limits [0, 1], the lower and/or
          upper bounds will be corrected to 0 and/or 1, respectively.
        * The cost_terms list must be a subset of {'voltage', 'dqdv', 'dvdq'}.
          When 'voltage' is included, an iR term is fit in addition to the
          x0/x100 terms. Otherwise, iR is forced towards zero.

        """

        for attr in ['_df_neg', '_df_pos', '_df_cell']:
            setattr(self, attr, None)

        if df_neg is not None:
            self.df_neg = df_neg

        if df_pos is not None:
            self.df_pos = df_pos

        if df_cell is not None:
            self.df_cell = df_cell

        self.smoothing = kwargs.pop('smoothing', 3)
        self.figure_font = kwargs.pop('figure_font', 10)
        self.bounds = kwargs.pop('bounds', [0.1] * 4)
        self.maxiter = kwargs.pop('maxiter', 1e5)
        self.xtol = kwargs.pop('xtol', 1e-9)
        self.cost_terms = kwargs.pop('cost_terms', ['dqdv', 'dvdq'])

        if len(kwargs) != 0:
            invalid_keys = list(kwargs.keys())
            raise ValueError(f"Invalid keyword arguments: {invalid_keys}")

    @property
    def df_neg(self) -> pd.DataFrame:
        """
        Get or set the negative electrode dataframe.

        Columns must include both 'soc' for state of charge and 'voltage' for
        the half-cell voltage. 'soc' should be normalized to [0, 1].

        """
        return self._df_neg

    @df_neg.setter
    def df_neg(self, value: pd.DataFrame) -> None:
        if not isinstance(value, pd.DataFrame):
            raise TypeError("df_neg must be type pd.DataFrame.")
        elif 'soc' not in value.columns:
            raise ValueError("'soc' is missing from df_neg.columns.")
        elif 'voltage' not in value.columns:
            raise ValueError("'voltage' is missing from df_neg.columns.")

        self._df_neg = value
        self.ocv_neg = self.ocv_spline(self._df_neg, 'neg')

    @property
    def df_pos(self) -> pd.DataFrame:
        """
        Get or set the positive electrode dataframe.

        Columns must include both 'soc' for state of charge and 'voltage' for
        the half-cell voltage. 'soc' should be normalized to [0, 1].

        """
        return self._df_pos

    @df_pos.setter
    def df_pos(self, value: pd.DataFrame) -> None:
        if not isinstance(value, pd.DataFrame):
            raise TypeError("df_pos must be type pd.DataFrame.")
        elif 'soc' not in value.columns:
            raise ValueError("'soc' is missing from df_pos.columns.")
        elif 'voltage' not in value.columns:
            raise ValueError("'voltage' is missing from df_pos.columns.")

        self._df_pos = value
        self.ocv_pos = self.ocv_spline(self._df_pos, 'pos')

    @property
    def df_cell(self) -> pd.DataFrame:
        """
        Get or set the full cell dataframe.

        Columns must include 'soc' for state of charge, 'voltage' for the cell
        voltage, 'dsoc_dV' for the derivative dsov/dV, and 'dV_dsoc' for the
        derivative dV/dsoc. 'soc' should be normalized to [0, 1].

        """
        return self._df_cell

    @df_cell.setter
    def df_cell(self, value: pd.DataFrame) -> None:
        import numpy as np

        if not isinstance(value, pd.DataFrame):
            raise TypeError("df_cell must be type pd.DataFrame.")
        elif 'soc' not in value.columns:
            raise ValueError("'soc' is missing from df_cell.columns.")
        elif 'voltage' not in value.columns:
            raise ValueError("'voltage' is missing from df_cell.columns.")
        elif 'dsoc_dV' not in value.columns:
            raise ValueError("'dsoc_dV' is missing from df_cell.columns.")
        elif 'dV_dsoc' not in value.columns:
            raise ValueError("'dV_dsoc' is missing from df_cell.columns.")

        self._df_cell = value
        output = self.ocv_spline(self._df_cell, 'cell')
        self.ocv_cell, self.dqdv_cell, self.dvdq_cell = output

        self._soc = np.linspace(0., 1., 500)
        self._soc_mid = 0.5 * (self._soc[:-1] + self._soc[1:])

        self.V_dat = self.ocv_cell(self._soc)
        self.dqdv_dat = self.dqdv_cell(self._soc_mid)
        self.dvdq_dat = self.dvdq_cell(self._soc_mid)

    @property
    def smoothing(self) -> int:
        """
        Get or set the fit smoothing.

        The fitted dsoc/dV and dV/dsoc curves often have a lot of noise in
        them because they carry noise over from both half-cell OCV curves.
        This property is used to smooth the fitted derivatives. The smoothed
        curves are used to determine error between the fit and data.

        """
        return self._smoothing

    @smoothing.setter
    def smoothing(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("smoothing must be type int.")

        self._smoothing = value

    @property
    def figure_font(self) -> int:
        """
        Get or set the figure fontsize.

        """
        return self._figure_font

    @figure_font.setter
    def figure_font(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("figure_font must be type int.")

        self._figure_font = value

    @property
    def bounds(self) -> list[float]:
        """
        Get or set the bounds for the constrained fit routine.

        """
        return self._bounds

    @bounds.setter
    def bounds(self, value: list[float]) -> None:
        if not isinstance(value, (list, tuple)):
            raise TypeError("bounds must be an iterable.")

        if len(value) != 4:
            raise ValueError("bounds must have length 4.")

        for v in value:
            if not isinstance(v, (float, int)):
                raise TypeError("All bounds[i] must be type float.")
            elif v < 0.001:
                raise ValueError("All bounds[i] must be >= 0.001.")
            elif v > 1.:
                raise ValueError("All bounds[i] must be <= 1.")

        self._bounds = value

    @property
    def maxiter(self) -> int:
        """
        Get or set the maximum iterations for the constrained fit routine.

        """
        return self._maxiter

    @maxiter.setter
    def maxiter(self, value: int) -> None:
        if isinstance(value, float):
            if not value.is_integer():
                raise TypeError("maxiter must be type int.")
            else:
                value = int(value)

        if not isinstance(value, int):
            raise TypeError("maxiter must be type int.")

        if value <= 0:
            raise ValueError("maxiter must be positive.")

        self._maxiter = value

    @property
    def xtol(self) -> float:
        """
        Get or set the 'x' tolerance for the constrained fit routine.

        """
        return self._xtol

    @xtol.setter
    def xtol(self, value: float) -> None:
        if not isinstance(value, (float, int)):
            raise TypeError("xtol must be type float.")

        if value <= 0.:
            raise ValueError("xtol must be positive.")

        self._xtol = value

    @property
    def cost_terms(self) -> list[str]:
        """
        Get or set which terms are included in the constrained fit's cost
        function. Options are 'voltage', 'dqdv', and/or 'dvdq'.

        """
        return self._cost_terms

    @cost_terms.setter
    def cost_terms(self, value: list[str]) -> None:
        if not isinstance(value, (list, tuple)):
            raise TypeError("cost_terms must be an iterable.")

        for v in value:
            if not isinstance(v, str):
                raise TypeError("All cost_terms[i] must be type str.")
            elif v not in ['voltage', 'dqdv', 'dvdq']:
                raise ValueError(f"Invalid cost term '{v}'. Valid options are"
                                 + " 'voltage', 'dqdv', and/or 'dvdq'.")

        if len(value) == 0:
            raise ValueError("len(cost_terms) == 0. Must include at least one"
                             + " of {'voltage', 'dqdv', 'dvdq'}.")

        self._cost_terms = value

    def ocv_spline(self, df: pd.DataFrame, name: str) -> callable:
        """
        Generate OCV interpolation functions.

        Parameters
        ----------
        df : pd.DataFrame
            Data with 'soc' and 'voltage' columns. If name is 'cell', the
            data should also include 'dsoc_dV' and 'dV_dsoc' columnes.
        name : str
            Dataset name, from {'neg', 'pos', 'cell'}.

        Returns
        -------
        ocv : callable
            If name is not 'cell' return a makima interpolation for OCV.
        ocv, dqdv, dvdq : tuple[callable]
            If name is 'cell', return a makima interpolation for OCV, dqdv,
            and dvdq.

        """

        from ..math import makima

        df = clean_df(df, unique_cols=['soc', 'voltage'], sort_by='soc')

        ocv = interp.CubicSpline(df.soc.values, df.voltage.values)

        if name == 'cell':
            dqdv_cell = makima(df.soc.values, df.dsoc_dV.values)
            dvdq_cell = makima(df.soc.values, df.dV_dsoc.values)
            return ocv, dqdv_cell, dvdq_cell
        else:
            return ocv

    def err_terms(self, params: np.ndarray,
                  full_output: bool = False) -> tuple[float] | dict:
        """
        Calculate error between the fit and data.

        Parameters
        ----------
        params : 1D np.array
            Array for x0_neg, x100_neg, x0_pos, x100_pos, and iR (optional).
        full_output : bool, optional
            Flag to return all data. The default is False.

        Returns
        -------
        errs : tuple[float]
            If full_output is False, return voltage error, dqdv error, and
            dvdq error values.
        full_output : dict
            If full_output is True, return a dictionary with the fit arrays,
            data arrays, and error values.

        Notes
        -----
        Error terms are the mean absolute errors between data and predicted
        values, normalized by the data. The normalization reduces preferences
        to fit any one cost term over others when more than one is considered.
        In addition, normalizing allows the errors to be added when the cost
        function includes more than one term.

        """

        if params.size == 5:
            x0_neg, x100_neg, x0_pos, x100_pos, iR = params
        else:
            x0_neg, x100_neg, x0_pos, x100_pos, iR = *params, 0.

        x_neg = x0_neg + (x100_neg - x0_neg) * self._soc
        x_pos = x0_pos + (x100_pos - x0_pos) * self._soc

        V_dat = self.V_dat
        V_fit = self.ocv_pos(x_pos) - self.ocv_neg(x_neg) - iR

        dqdv_dat = self.dqdv_dat
        dqdv_fit = np.diff(self._soc) / np.diff(V_fit)
        dqdv_fit = savgol_filter(dqdv_fit, self.smoothing, 2, mode='nearest')

        dvdq_dat = self.dvdq_dat
        dvdq_fit = np.diff(V_fit) / np.diff(self._soc)
        dvdq_fit = savgol_filter(dvdq_fit, self.smoothing, 2, mode='nearest')

        err1 = np.mean(np.abs((V_fit - V_dat) / V_dat))
        err2 = np.mean(np.abs((dqdv_fit - dqdv_dat) / dqdv_dat))
        err3 = np.mean(np.abs((dvdq_fit - dvdq_dat) / dvdq_dat))

        if not full_output:
            return err1, err2, err3

        else:
            output = {
                'soc': self._soc,
                'soc_mid': self._soc_mid,
                'V_dat': V_dat,
                'V_fit': V_fit,
                'dqdv_dat': dqdv_dat,
                'dqdv_fit': dqdv_fit,
                'dvdq_dat': dvdq_dat,
                'dvdq_fit': dvdq_fit,
                'err1': err1,
                'err2': err2,
                'err3': err3,
            }

            return output

    def err_func(self, params: np.ndarray) -> float:
        """
        The cost function for coarse_search and constrained_fit.

        Parameters
        ----------
        params : 1D np.array
            Array for x0_neg, x100_neg, x0_pos, x100_pos, and iR (optional).

        Returns
        -------
        err_tot : float
            Total error based on a combination of cost_terms.

        """

        err1, err2, err3 = self.err_terms(params)

        err = 0.
        if 'voltage' in self.cost_terms:
            err += err1

        if 'dqdv' in self.cost_terms:
            err += err2

        if 'dvdq' in self.cost_terms:
            err += err3

        return err

    def coarse_search(self, Nx: int) -> dict:
        """
        Determine the minimum error by evaluating parameter sets taken from
        intersections of a coarse grid. Parameter sets where x0 < x100 for
        either electrode are ignored.

        Parameters
        ----------
        Nx : int
            Number of discretizations between [0, 1] for each parameter.

        Returns
        -------
        summary : dict
            Summarized results from the coarse search.

        """

        from ..math import combinations

        span = np.linspace(0., 1., Nx)
        names = ['x0_neg', 'x100_neg', 'x0_pos', 'x100_pos']

        params = combinations([span] * 4, names=names)

        valid_ps = []
        for p in params:
            if p['x0_neg'] < p['x100_neg'] and p['x0_pos'] < p['x100_pos']:
                valid_ps.append(p)

        errs = []
        for p in valid_ps:
            values = np.array(list(p.values()))
            errs.append(self.err_func(values))

        index = np.argmin(errs)

        summary = {'nfev': len(errs),
                   'fun': errs[index],
                   'x': np.array(list(valid_ps[index].values())),
                   'x_map': list(valid_ps[index].keys())
                   }

        return summary

    def constrained_fit(self, x0: np.ndarray) -> dict:
        """
        Run a trust-constrained local optimization routine to minimize error
        between the fit and data.

        Parameters
        ----------
        x0 : 1D np.array
            Initial x0_neg, x100_neg, x0_pos, x100_pos, iR (optional) values.

        Returns
        -------
        summary : dict
            Summarized results from the optimization routine.

        """

        x0 = x0.copy()

        output = self.err_terms(x0, full_output=True)

        iR0 = (output['V_fit'] - output['V_dat']).mean()

        if x0.size == 5:
            x0[-1] = iR0
        elif x0.size == 4:
            x0 = np.hstack([x0, iR0])

        lower = np.zeros_like(x0)
        upper = np.ones_like(x0)
        for i in range(4):
            lower[i] = max(0., x0[i] - self.bounds[i])
            upper[i] = min(1., x0[i] + self.bounds[i])

        if 'voltage' in self._cost_terms:
            lower[-1] = -np.inf
            upper[-1] = np.inf
        else:
            lower[-1] = 0.
            upper[-1] = 0.

        bounds = [(L, U) for L, U in zip(lower, upper)]

        constr_neg = opt.LinearConstraint([[1, -1, 0, 0, 0]], -np.inf, 0.)
        constr_pos = opt.LinearConstraint([[0, 0, 1, -1, 0]], -np.inf, 0.)
        constr_iR = opt.LinearConstraint([[0, 0, 0, 0, 1]], *bounds[-1])

        constraints = [constr_neg, constr_pos, constr_iR]

        options = {
            'maxiter': self.maxiter,
            'xtol': self.xtol,
        }

        warnings.filterwarnings('ignore')

        result = opt.minimize(self.err_func, x0, method='trust-constr',
                              bounds=bounds, constraints=constraints,
                              options=options)

        warnings.filterwarnings('default')

        keys = ['success', 'message', 'nfev', 'niter', 'fun', 'x']
        summary = dict((k, result[k]) for k in keys)

        summary['x_map'] = ['x0_neg', 'x100_neg', 'x0_pos', 'x100_pos', 'iR']

        return summary

    def plot(self, params: np.ndarray, **kwargs) -> None:
        """
        Plot the fit vs. data.

        Parameters
        ----------
        params : 1D np.array
            Parameter array x0_neg, x100_neg, x0_pos, x100_pos, iR (optional).
        **kwargs : dict, optional
            Keyword arguments. Optional key/value pairs are below:

            ============== ============================================
            Key            Value (*type*, default)
            ============== ============================================
            fig            1x3 subplot figure to fill (*object*, None)
            voltage_ylims  ylimits for voltage (*list[float]*, None)
            dqdv_ylims     ylimits for dsoc_dV (*list[float]*, None)
            dvdq_ylims     ylimits for dV_dsoc (*list[float]*, None)
            ============== ============================================

        Returns
        -------
        None.

        """

        from ..plotutils import format_ticks, add_text

        fig = kwargs.pop('fig', None)
        figsize = kwargs.pop('figsize', [12., 3.])

        plt.rcParams['font.size'] = self.figure_font

        if fig is None:
            fig, ax = plt.subplots(nrows=1, ncols=3, figsize=figsize,
                                   layout='tight')
        else:
            ax = fig.get_axes()
            _ = [ax[i].clear() for i in range(3)]

        output = self.err_terms(params, full_output=True)

        dat_options = {'color': 'C1', 'linestyle': '', 'alpha': 0.5,
                       'marker': 'o', 'label': 'Data'}

        fit_options = {'color': 'k', 'linestyle': '-', 'label': 'Model'}

        ax[0].set_ylabel('Voltage [V]')
        ax[0].plot(output['soc'], output['V_dat'], **dat_options)
        ax[0].plot(output['soc'], output['V_fit'], **fit_options)
        add_text(ax[0], 0.1, 0.8, f"{output['err1']:.3e}")

        ax[1].set_ylabel(r'$dq/dV$ [V$^{-1}$]')
        ax[1].plot(output['soc_mid'], output['dqdv_dat'], **dat_options)
        ax[1].plot(output['soc_mid'], output['dqdv_fit'], **fit_options)
        add_text(ax[1], 0.6, 0.8, f"{output['err2']:.3e}")

        ax[2].set_ylabel(r'$dV/dq$ [V]')
        ax[2].plot(output['soc_mid'], output['dvdq_dat'], **dat_options)
        ax[2].plot(output['soc_mid'], output['dvdq_fit'], **fit_options)
        add_text(ax[2], 0.6, 0.8, f"{output['err3']:.3e}")

        ax[0].legend(loc='lower right', frameon=False)

        if 'voltage_ylims' in kwargs.keys():
            ax[0].set_ylim(kwargs.get('voltage_ylims'))

        if 'dqdv_ylims' in kwargs.keys():
            ax[1].set_ylim(kwargs.get('dqdv_ylims'))

        if 'dvdq_ylims' in kwargs.keys():
            ax[2].set_ylim(kwargs.get('dvdq_ylims'))

        for i in range(3):
            format_ticks(ax[i])
            ax[i].set_xlabel(r'SOC, $q$ [$-$]')


def clean_df(df: pd.DataFrame, unique_cols: list[str] = [],
             sort_by: str = None) -> pd.DataFrame:
    """
    Clean up dataframes for dqdv analysis.

    Drop all nan values, ensure specified columns do not have duplicates,
    and sort the whole dataframe according to a given column.

    Parameters
    ----------
    df : pd.DataFrame
        A pandas dataframe.
    unique_cols : list[str], optional
        Columns to remove duplicate values, if present. The default is [].
    sort_by : str, optional
        Column name used to sort dataframe. The default is None.

    Returns
    -------
    df : pd.DataFrame
        Cleaned and sorted dataframe.

    """

    for col in unique_cols:
        _, mask = np.unique(df[col], return_index=True)
        df = df.iloc[mask]

    df = df.dropna()
    if sort_by is not None:
        df = df.sort_values(sort_by)

    df = df.reset_index(drop=True)

    return df


def preprocess_df(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    from ..math import dydx, makima

    sw = kwargs.get('smoothing_win', None)
    V_lower = kwargs.get('V_lower', min(df.voltage))
    V_upper = kwargs.get('V_upper', max(df.voltage))
    V_res = kwargs.get('V_res', 1e-3)
    capacity = kwargs.get('capacity', max(abs(df.amphr)))
    flip_amphr = kwargs.get('flip_amphr', False)

    df = clean_df(df, unique_cols=['voltage', 'amphr'], sort_by='voltage')

    data = {}

    voltage = np.arange(V_lower, V_upper, V_res)
    data['voltage'] = voltage

    amphr_func = makima(df.voltage, df.amphr)
    amphr = np.abs(amphr_func(voltage))

    if flip_amphr:
        amphr = capacity - amphr

    data['amphr'] = amphr
    data['soc'] = amphr / capacity

    options = {'smoothing_win_y': sw, 'lead_value': np.nan}
    data['damphr_dV'] = dydx(data['voltage'], data['amphr'], **options)
    data['dsoc_dV'] = dydx(data['voltage'], data['soc'], **options)

    options = {'smoothing_win_x': sw, 'lead_value': np.nan}
    data['dV_damphr'] = dydx(data['amphr'], data['voltage'], **options)
    data['dV_dsoc'] = dydx(data['soc'], data['voltage'], **options)

    if 'time' in df.columns:
        time_func = makima(df.voltage, df.time)
        data['time'] = time_func(data['voltage'])

    if 'current' in df.columns:
        current_func = makima(df.voltage, df.current)
        data['current'] = current_func(data['voltage'])

    output = pd.DataFrame(data)

    return output


def post_process(capacity: np.ndarray, x: np.ndarray) -> dict:
    """
    Determine degradation parameters.

    Uses full cell capacity and fitted x0/x100 values from dqdv/dvdq fits to
    calculate theoretical electrode capacities, loss of active material (LAM),
    and total inventory losses (TIL). TIL is used instead of LLI (loss of
    lithium inventory) because this analysis is also valid for intercalation
    electrodes with active species other than lithium.

    Electrode capacities (Q) and losses of active material (LAM) are

    .. math::

        Q_{\rm ed} = \frac{\rm capacity}{x_{100, \rm ed} - x_{0, \rm ed}}, \\
        {\rm LAM}_{\rm ed} = 1 - \frac{Q_{\rm ed}}{Q_{\rm ed}[0]},

    where :math:`ed` is used generically 'electrode'. In the output, subscripts
    'neg' and 'pos' are used to differentiate between the negative and positive
    electrodes, respectively. Loss of inventory is

    .. math::

        I = x_{100, \rm neg}Q_{\rm neg} + x_{100, \rm pos}Q_{\rm pos}, \\
        {\rm TIL} = 1 - \frac{I}{I[0]},

    where :math:`I` is an array of inventories calculated from the capacities
    :math:`Q` above. The 'offset' output can also sometimes serve as a helpful
    metric. It is simply the difference between 'x0_neg' and 'x0_pos'.

    Parameters
    ----------
    capacity : 1D np.array
        Full cell capacity values per fitted profile.
    x : 2D np.array
        Fitted x0/x100 values. Row i corresponds to capacity[i], with column
        order: x0_neg, x100_neg, x0_pos, x100_pos.

    Raises
    ------
    ValueError
        capacity.size != x.shape[0].
    ValueError
        x.shape[1] != 4.

    Returns
    -------
    results : dict
        Electrode capacities (Q) and loss of active material (LAM) for the
        negative (neg) and positive (pos) electrodes, and total loss of
        intentory (TLI). Capacity units match the ``capacity`` input. All
        other outputs are unitless.

    """

    if capacity.size != x.shape[0]:
        raise ValueError(f"{capacity.size=} != {x.shape[0]=}.")

    if x.shape[1] == 4:
        x0_neg, x100_neg, x0_pos, x100_pos = x.T
    else:
        raise ValueError(f"{x.shape[1]=} != 4.")

    Q_neg = capacity / (x100_neg - x0_neg)
    Q_pos = capacity / (x100_pos - x0_pos)

    offset = x0_neg - x0_pos

    LAM_neg = 1. - Q_neg / Q_neg[0]
    LAM_pos = 1. - Q_pos / Q_pos[0]

    inventory = x100_neg*Q_neg + (1. - x100_pos)*Q_pos
    TIL = 1. - inventory / inventory[0]

    results = {
        'Q_neg': Q_neg,
        'Q_pos': Q_pos,
        'offset': offset,
        'LAM_neg': LAM_neg,
        'LAM_pos': LAM_pos,
        'TIL': TIL,
    }

    return results


def run_gui() -> None:
    """
    Run a graphical interface for the Fitter class.

    Returns
    -------
    None.

    """

    from .gui_files import _gui

    _gui.run()
