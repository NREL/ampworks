from __future__ import annotations

import warnings

from numbers import Real
from typing import Callable, Iterable, TYPE_CHECKING

import numpy as np
import pandas as pd
import scipy.optimize as opt
import matplotlib.pyplot as plt
import scipy.interpolate as interp

if TYPE_CHECKING:  # pragma: no cover
    import numpy.typing as npt

    from ampworks.utils import RichResult


class DqdvFitter:

    def __init__(
        self, neg: pd.DataFrame = None, pos: pd.DataFrame = None,
        cell: pd.DataFrame = None, cost_terms: str | list[str] = 'all',
    ) -> None:
        """
        Wrapper for dQ/dV fitting.

        TODO: detailed description for dQ/dV fitting class.

        Parameters
        ----------
        neg : pd.DataFrame
            Negative electrode OCV data.
        pos : pd.DataFrame
            Positive electrode OCV data.
        cell : pd.DataFrame
            Full cell OCV data.
        cost_terms : str or list[str], optional
            Error terms for optimization. 'all' (default) = ['voltage', 'dqdv',
            'dvdq']. Accepts a string (single term) or list (subset of terms).

        Notes
        -----
        * The dataframe inputs are all required. The default ``None`` values
          allow you to initialize the class first and add each one at a time.
          This is primarily to support interactions with the GUI.
        * When 'voltage' is included in ``cost_terms``, an iR term is fit in
          addition to the x0/x1 stoichiometries. Otherwise, the ohmic iR offset
          is forced to 0. ``cost_terms`` can be modified after initialization
          via its property.

        References
        ----------
        TODO

        """

        self._initialized = {'neg': False, 'pos': False, 'cell': False}

        self.neg = neg
        self.pos = pos
        self.cell = cell

        self.cost_terms = cost_terms

    @property
    def neg(self) -> pd.DataFrame:
        """
        Get or set the negative electrode dataframe.

        Columns must include both 'soc' for state of charge and 'voltage' for
        the half-cell voltage. 'soc' should be normalized to [0, 1].

        """
        return self._neg

    @neg.setter
    def neg(self, value: pd.DataFrame) -> None:

        required = {'soc', 'voltage'}
        if value is None:
            pass
        elif not isinstance(value, pd.DataFrame):
            raise TypeError("'neg' must be type pd.DataFrame.")
        elif not required.issubset(value.columns):
            raise ValueError(f"'neg' is missing columns, {required=}.")

        self._neg = value
        self._ocv_n, self._dvdq_n = self._build_splines(self._neg, 'neg')

    @property
    def pos(self) -> pd.DataFrame:
        """
        Get or set the positive electrode dataframe.

        Columns must include both 'soc' for state of charge and 'voltage' for
        the half-cell voltage. 'soc' should be normalized to [0, 1].

        """
        return self._pos

    @pos.setter
    def pos(self, value: pd.DataFrame) -> None:

        required = {'soc', 'voltage'}
        if value is None:
            pass
        elif not isinstance(value, pd.DataFrame):
            raise TypeError("'pos' must be type pd.DataFrame.")
        elif not required.issubset(value.columns):
            raise ValueError(f"'pos' is missing columns, {required=}.")

        self._pos = value
        self._ocv_p, self._dvdq_p = self._build_splines(self._pos, 'pos')

    @property
    def cell(self) -> pd.DataFrame:
        """
        Get or set the full cell dataframe.

        Columns must include 'soc' for state of charge, 'voltage' for the cell
        voltage, 'dsoc_dV' for the derivative dsov/dV, and 'dV_dsoc' for the
        derivative dV/dsoc. 'soc' should be normalized to [0, 1].

        """
        return self._cell

    @cell.setter
    def cell(self, value: pd.DataFrame) -> None:

        required = {'soc', 'voltage'}
        if value is None:
            pass
        elif not isinstance(value, pd.DataFrame):
            raise TypeError("'cell' must be type pd.DataFrame.")
        elif not required.issubset(value.columns):
            raise ValueError(f"'cell' is missing columns, {required=}.")

        self._cell = value
        self._ocv_c, self._dvdq_c = self._build_splines(self._cell, 'cell')

        if self._initialized['cell']:
            self._soc = np.linspace(0., 1., 201)

            self._volt_data = self._ocv_c(self._soc)
            self._dvdq_data = self._dvdq_c(self._soc)
            self._dqdv_data = 1 / self._dvdq_data

    @property
    def cost_terms(self) -> list[str]:
        """
        Get or set which terms are included in the constrained fit's cost
        function. Options are 'voltage', 'dqdv', and/or 'dvdq'. You can also
        set to 'all' to conveniently select all three cost terms.

        """
        return self._cost_terms

    @cost_terms.setter
    def cost_terms(self, value: str | list[str]) -> None:

        options = ['voltage', 'dqdv', 'dvdq']

        if value == 'all':
            value = options.copy()
        elif isinstance(value, str):
            value = [value]

        if not isinstance(value, Iterable):
            raise TypeError("cost_terms must be an iterable.")

        if len(value) == 0:
            raise ValueError("cost_terms is empty. Set to either 'all' or a"
                             f"subset of of {options}.")

        if not set(value).issubset(options):
            raise ValueError("cost_terms has at least one invalid value. It"
                             f" can only be 'all' or a subset of {options}.")

        self._cost_terms = value

    def _build_splines(self, df: pd.DataFrame, domain: str) -> Callable:
        """
        Generate OCV interpolation functions.

        Parameters
        ----------
        df : pd.DataFrame
            Data with 'soc' and 'voltage' columns.
        domain : str
            Which domain splines are being built, from ['neg', 'pos', 'cell'].
            Used to track when initialization is complete.

        Returns
        -------
        ocv, dvdq : tuple[Callable]
            Spline interpolations for ocv and dvdq.

        """

        if df is None:
            return None, None

        _, mask = np.unique(df.soc, return_index=True)

        df = df.iloc[mask].reset_index(drop=True)

        ocv = interp.make_splrep(df.soc, df.voltage)
        dvdq = ocv.derivative()

        self._initialized[domain] = True

        return ocv, dvdq

    def _check_initialized(self, func_name: str) -> None:
        """
        Check that the instance is fully initialized, will all splines and
        data for 'neg', 'pos', and 'cell'. If any is missing raise an error.

        Parameters
        ----------
        func_name : str
            Name of function performing check.

        Raises
        ------
        RuntimeError
            Can't run any functions until all data is available.

        """

        missing = [d for d, flag in self._initialized.items() if not flag]
        if missing:
            raise RuntimeError(f"Can't run '{func_name}' until all data is"
                               f" available. Missing {missing} data.")

    def _err_func(self, params: npt.ArrayLike) -> float:
        """
        The cost function for 'grid_search' and 'constrained_fit'.

        Parameters
        ----------
        params : ArrayLike, shape(n,)
            Array for xn0, xn1, xp0, xp1, and optionally iR.

        Returns
        -------
        err_total : float
            Total error based on a combination of cost_terms.

        """

        errs = self.err_terms(params)

        err_total = 0.  # faster when MAP is fractional, so use (*1e-2) below
        if 'voltage' in self.cost_terms:
            err_total += errs['volt_err']*1e-2
        if 'dqdv' in self.cost_terms:
            err_total += errs['dqdv_err']*1e-2
        if 'dvdq' in self.cost_terms:
            err_total += errs['dvdq_err']*1e-2

        return err_total

    def get_ocv(self, domain: str, soc: npt.ArrayLike) -> npt.ArrayLike:
        """
        Evaluate the OCV spline for the specified domain.

        Parameters
        ----------
        which : {'neg', 'pos', 'cell'}
            Which OCV spline to evaluate.
        x : ArrayLike
            Stoichiometry or SOC values to evaluate at.

        Returns
        -------
        ocv : np.ndarray
            Evaluated OCV values.

        Raises
        ------
        ValueError
            'domain' must be in ['neg', 'pos', 'cell'].
        RuntimeError
            If the requested spline has not yet been constructed.

        """

        if domain not in ['neg', 'pos', 'cell']:
            raise ValueError("'domain' must be in ['neg', 'pos', 'cell'].")

        spline = getattr(self, f"_ocv_{domain[0]}")
        if spline is None:
            raise RuntimeError(f"'{domain}' splines are not constructed yet."
                               f" Set the '{domain}' property first.")

        return spline(soc)

    def get_dvdq(self, domain: str, soc: npt.ArrayLike) -> npt.ArrayLike:
        """
        Evaluate the dV/dq spline for the specified domain.

        Parameters
        ----------
        which : {'neg', 'pos', 'cell'}
            Which dV/dq spline to evaluate.
        x : ArrayLike
            Stoichiometry or SOC values to evaluate at.

        Returns
        -------
        dvdq : np.ndarray
            Evaluated dV/dq values.

        Raises
        ------
        ValueError
            'domain' must be in ['neg', 'pos', 'cell'].
        RuntimeError
            If the requested spline has not yet been constructed.

        """

        if domain not in ['neg', 'pos', 'cell']:
            raise ValueError("'domain' must be in ['neg', 'pos', 'cell'].")

        spline = getattr(self, f"_dvdq_{domain[0]}")
        if spline is None:
            raise RuntimeError(f"'{domain}' splines are not constructed yet."
                               f" Set the '{domain}' property first.")

        return spline(soc)

    def get_dqdv(self, domain: str, soc: npt.ArrayLike) -> npt.ArrayLike:
        """
        Evaluate the dq/dV spline for the specified domain.

        Parameters
        ----------
        which : {'neg', 'pos', 'cell'}
            Which dq/dV spline to evaluate.
        x : ArrayLike
            Stoichiometry or SOC values to evaluate at.

        Returns
        -------
        dvdq : np.ndarray
            Evaluated dq/dV values.

        Raises
        ------
        ValueError
            'domain' must be in ['neg', 'pos', 'cell'].
        RuntimeError
            If the requested spline has not yet been constructed.

        """
        return 1 / self.get_dvdq(domain, soc)

    def err_terms(self, params: npt.ArrayLike) -> RichResult:
        """
        Calculate error between the fit and data.

        Parameters
        ----------
        params : ArrayLike, shape(n,)
            Array for xn0, xn1, xp0, xp1, and iR (optional). If you already
            performed a fit you can simply use ``summary.x``.

        Returns
        -------
        errs : RichResult
            Voltage, dqdv, and dvdq errors. The soc, fit, and data arrays are
            also included for convenience and plotting.

        Notes
        -----
        Error are calculated as mean absolute percent errors between the data
        and fits. The normalization reduces preferences to fit any one cost
        term over others when more than one is considered. It also removes any
        units so it is more mathematically correct to sum the errors.

        """
        from ampworks.utils import RichResult

        self._check_initialized('err_terms')

        params = np.asarray(params)
        params[:4] = np.clip(params[:4], 0., 1.)

        if params.size == 5:
            xn0, xn1, xp0, xp1, iR = params
        else:
            xn0, xn1, xp0, xp1, iR = *params, 0.

        x_neg = xn0 + (xn1 - xn0) * self._soc
        x_pos = xp0 + (xp1 - xp0) * self._soc

        dxp_dx = xp1 - xp0  # for chain rule w.r.t. x_pos -> soc below
        dxn_dx = xn1 - xn0  # for chain rule w.r.t. x_neg -> soc below

        volt_fit = self._ocv_p(x_pos) - self._ocv_n(x_neg) - iR

        dvdq_fit = self._dvdq_p(x_pos)*dxp_dx - self._dvdq_n(x_neg)*dxn_dx
        dqdv_fit = 1 / dvdq_fit

        volt_data = self._volt_data
        dqdv_data = self._dqdv_data
        dvdq_data = self._dvdq_data

        volt_err = np.mean(np.abs((volt_fit - volt_data) / volt_data))
        dqdv_err = np.mean(np.abs((dqdv_fit - dqdv_data) / dqdv_data))
        dvdq_err = np.mean(np.abs((dvdq_fit - dvdq_data) / dvdq_data))

        errs = RichResult(
            soc=self._soc,
            volt_err=volt_err*100,
            volt_fit=volt_fit,
            volt_data=volt_data,
            dqdv_err=dqdv_err*100,
            dqdv_fit=dqdv_fit,
            dqdv_data=dqdv_data,
            dvdq_err=dvdq_err*100,
            dvdq_fit=dvdq_fit,
            dvdq_data=dvdq_data,
        )

        return errs

    def grid_search(self, Nx: int) -> dict:
        """
        Determine the minimum error by evaluating parameter sets taken from
        intersections of a coarse grid. Parameter sets where either x0 < x1
        are ignored.

        Parameters
        ----------
        Nx : int
            Number of discretizations between [0, 1] for each parameter.

        Returns
        -------
        summary : dict
            Summarized results from the grid search.

        """
        from ampworks.utils import RichResult
        from ampworks.mathutils import combinations

        self._check_initialized('grid_search')

        span = np.linspace(0., 1., Nx)
        names = ['xn0', 'xn1', 'xp0', 'xp1', 'iR']

        params = combinations([span] * 4, names=names)

        valid_ps = []
        for p in params:
            if p['xn0'] < p['xn1'] and p['xp0'] < p['xp1']:
                valid_ps.append(p)

        errs = np.zeros(len(valid_ps))
        for i, p in enumerate(valid_ps):
            values = np.fromiter(p.values(), dtype=float)
            errs[i] = self._err_func(values)

        index = np.argmin(errs)
        x_opt = np.fromiter(valid_ps[index].values(), dtype=float)

        summary = RichResult(
            success=True,
            message='Done searching.',
            nfev=len(errs),
            niter=None,
            fun=errs[index],
            x=np.hstack([x_opt, 0.]),
            x_std=np.repeat(np.nan, 5),
            x_map=names,
        )

        return summary

    def constrained_fit(
        self, x0: npt.ArrayLike, bounds: float | list[float] = 0.1,
        xtol: float = 1e-8, maxiter: int = 1e5, return_full: bool = False,
    ) -> RichResult:
        """
        Run a trust-constrained local optimization routine to minimize error
        between the fit and data.

        Parameters
        ----------
        x0 : ArrayLike, shape(n,)
            Initial xn0, xn1, xp0, xp1, and optionally iR. If you already ran
            a previous fit you can simply use ``summary.x``.
        bounds : float or list[float], optional
            Symmetric parameter bounds (excludes iR). A float (default=0.1)
            applies to all. Use lists for per-x values. See notes for more info.
        xtol : float, optional
            Convergence tolerance for parameters. Defaults to 1e-8.
        maxiter : int, optional
            Maximum number of iteraterations. Defaults to 1e5.
        return_full : bool, optional
            If True, include the complete ``OptimizeResult`` from SciPy in the
            output. Defaults to False.

        Returns
        -------
        summary : RichResult
            A subset summary of SciPy's optimization results, including an added
            approximate standard deviation for the pameters.
        optresult : OptimizeResult
            Full result form SciPy. Does not include standard deviation info.
            Only returned if ``return_full=True``.

        Notes
        -----
        Bound indices correspond to xn0, xn1, xp0, and xp1, where 0 and 1 are
        in reference to lower and upper stoichiometries of the negative (n)
        and positive (p) electrodes. Set ``bounds[i] = 1`` to disable bounds and
        use the full interval [0, 1] for x[i]. If an ``x[i] +/- bounds[i]``
        exceeds [0, 1], the lower and/or upper bounds will be corrected to 0
        and/or 1, respectively. Furthermore, bounds are clipped to be between
        0.001 and 1 behind the scenes. It does not help to use values outside
        this range.

        The ``summary`` output contains uncertainty estimates for the fitted
        parameters. These are approximated from the numerical Hessian at the
        optimum. The method assumes the function is locally linear, the input
        errors are independent and small, and the fit is well-behaved. Notes
        on the method are available `here <https://max.pm/posts/hessian_ls/>`.

        Because these assumptions do not always hold, the uncertainties can
        sometimes appear large or misleading, even when the fit is good. The
        estimates also depend on the quality of the data and the fit. Users
        should judge when to trust the uncertainty values, based on fit quality
        and the relative magnitudes of the reported estimates.

        """
        from numdifftools import Hessian
        from ampworks.utils import RichResult

        self._check_initialized('constrained_fit')

        x0 = np.asarray(x0)
        eps = np.finfo(x0.dtype).eps

        # check and build bounds
        if isinstance(bounds, Real):
            bounds = [bounds]*4

        if not isinstance(bounds, Iterable):
            raise TypeError("'bounds' must be an iterable.")

        if len(bounds) != 4:
            raise ValueError("'bounds' must have length 4.")

        errs = self.err_terms(x0)

        iR0 = (errs['volt_fit'] - errs['volt_data']).mean()

        if x0.size == 5:
            x0[-1] = iR0
        elif x0.size == 4:
            x0 = np.hstack([x0, iR0])

        lower = np.zeros_like(x0)
        upper = np.ones_like(x0)
        bounds = np.clip(bounds, 1e-3, 1.)
        for i in range(4):
            lower[i] = max(0., x0[i] - bounds[i])
            upper[i] = min(1., x0[i] + bounds[i])

        if 'voltage' in self.cost_terms:
            lower[-1] = -np.inf
            upper[-1] = np.inf
        else:
            lower[-1] = -eps
            upper[-1] = eps

        bounds = [(L, U) for L, U in zip(lower, upper)]

        # constrain each x0 < x1
        constr_neg = opt.LinearConstraint([[1, -1, 0, 0, 0]], -np.inf, 0.)
        constr_pos = opt.LinearConstraint([[0, 0, 1, -1, 0]], -np.inf, 0.)

        constraints = [constr_neg, constr_pos]

        options = {
            'xtol': xtol,
            'maxiter': maxiter,
        }

        warnings.filterwarnings('ignore')

        result = opt.minimize(self._err_func, x0, method='trust-constr',
                              bounds=bounds, constraints=constraints,
                              options=options)

        warnings.filterwarnings('default')

        # Use Hessian to approximate variance, standard deviation. This follows
        #     notes from https://max.pm/posts/hessian_ls/. The added scaling
        #     helps make sure the inversion is stable (non singular).

        def bounded_ssr(x):  # sum of squared residuals

            errs = self.err_terms(x)

            volt_err = (errs['volt_fit'] - self._volt_data)**2
            dqdv_err = (errs['dqdv_fit'] - self._dqdv_data)**2
            dvdq_err = (errs['dvdq_fit'] - self._dvdq_data)**2

            ssr = 0.
            if 'voltage' in self.cost_terms:
                ssr += volt_err.sum()
            if 'dqdv' in self.cost_terms:
                ssr += dqdv_err.sum()
            if 'dvdq' in self.cost_terms:
                ssr += dvdq_err.sum()

            return ssr

        result.hess = Hessian(bounded_ssr)(result.x)

        evals, _ = np.linalg.eig(result.hess)
        scale = 1e-16*np.max(np.abs(evals))

        try:
            cov = np.linalg.inv(result.hess + scale*np.eye(result.x.size))
            std = np.sqrt(np.abs(np.diag(cov)))
        except Exception:
            std = None

        if 'voltage' not in self.cost_terms:
            result.x[-1] = 0.

            if std is not None:
                std[-1] = 0.

        summary = RichResult(
            success=result.success,
            message=result.message,
            nfev=result.nfev,
            niter=result.niter,
            fun=result.fun,
            x=result.x,
            x_std=std,
            x_map=['xn0', 'xn1', 'xp0', 'xp1', 'iR'],
        )

        if return_full:
            return summary, result

        return summary

    def plot(self, params: npt.ArrayLike) -> None:
        """
        Plot the model fit vs. data.

        Parameters
        ----------
        params : ArrayLike, shape(n,)
            Array for xn0, xn1, xp0, xp1, and iR (optional). If you already
            performed a fit you can simply use ``summary.x``.

        Returns
        -------
        None.

        """
        from ampworks.plotutils import add_text, format_ticks, focused_limits

        self._check_initialized('plot')

        xn0, xn1, xp0, xp1 = params[:4]
        errs = self.err_terms(params)

        fig = plt.figure(figsize=[9.0, 3.75], constrained_layout=True)
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 1])

        ax1 = fig.add_subplot(gs[:, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 1])

        pstyle = {'ls': '-', 'lw': 2, 'color': 'C3', 'label': 'Pos'}
        nstyle = {'ls': '-', 'lw': 2, 'color': 'C0', 'label': 'Neg'}
        mstyle = {'ls': '-', 'lw': 2, 'color': 'k', 'label': 'Model'}
        dstyle = {'ls': '', 'ms': 7, 'marker': 'o', 'mfc': 'grey',
                  'alpha': 0.3, 'markeredgecolor': 'k', 'label': 'Data'}

        lines = []

        # ax1: pos, neg, model, and data voltages -----------------------------
        data = ax1.plot(errs['soc'][::5], errs['volt_data'][::5], **dstyle)
        model = ax1.plot(errs['soc'], errs['volt_fit'], **mstyle)

        lines.extend(data)
        lines.extend(model)

        socp = (errs['soc'] - xp0) / (xp1 - xp0)
        pos = ax1.plot(socp, self._ocv_p(errs['soc']), **pstyle)

        lines.extend(pos)

        twin = ax1.twinx()
        socn = (errs['soc'] - xn0) / (xn1 - xn0)
        neg = twin.plot(socn, self._ocv_n(errs['soc']), **nstyle)

        lines.extend(neg)

        # Vertical lines
        ax1.axvline(0., linestyle='--', color='grey')
        ax1.axvline(1., linestyle='--', color='grey')

        add_text(ax1, 0.5, 0.06, f"MAP={errs['volt_err']:.2e}%", ha='center')

        ax1.set_xlabel(r"q [$-$]")
        ax1.set_ylabel(r"Voltage (pos/cell) [V]")
        twin.set_ylabel(r"Voltage (neg) [V]")

        ax1.legend(lines, [line.get_label() for line in lines], ncols=2,
                   loc='upper center', frameon=False)

        # ax2: dqdv -----------------------------------------------------------
        ax2.plot(errs['soc'], errs['dqdv_fit'], zorder=10, **mstyle)
        ax2.plot(errs['soc'][::3], errs['dqdv_data'][::3], **dstyle)

        add_text(ax2, 0.6, 0.85, f"MAP={errs['dqdv_err']:.2e}%")

        ax2.set_xticklabels([])
        ax2.set_ylabel(r"dq/dV [1/V]")

        # ax3: dvdq -----------------------------------------------------------
        ax3.plot(errs['soc'], errs['dvdq_fit'], zorder=10, **mstyle)
        ax3.plot(errs['soc'][::3], errs['dvdq_data'][::3], **dstyle)

        add_text(ax3, 0.6, 0.85, f"MAP={errs['dvdq_err']:.2e}%")

        ax3.set_xlabel(r"q [$-$]")
        ax3.set_ylabel(r"dV/dq [V]")

        dvdq = np.hstack([errs['dvdq_data'], errs['dvdq_fit']])
        ylims = focused_limits(dvdq)
        ax3.set_ylim(ylims)

        # additional formatting
        format_ticks(ax1, xdiv=2, ydiv=2, right=False)  # separate b/c twinx

        for ax in [twin, ax2, ax3]:
            format_ticks(ax, xdiv=2, ydiv=2)

    # TODO: ExitHandler - register plt.show()
