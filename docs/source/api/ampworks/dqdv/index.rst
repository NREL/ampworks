ampworks.dqdv
=============

.. py:module:: ampworks.dqdv

.. autoapi-nested-parse::

   .. rubric:: TODO



Classes
-------

.. autoapisummary::

   ampworks.dqdv.Fitter


Functions
---------

.. autoapisummary::

   ampworks.dqdv.clean_df
   ampworks.dqdv.post_process
   ampworks.dqdv.run_gui


Package Contents
----------------

.. py:class:: Fitter(df_neg = None, df_pos = None, df_cell = None, **kwargs)

   
   Wrapper class for differential analysis.

   :param df_neg: Data for negative electrode OCV.
   :type df_neg: pd.DataFrame
   :param df_pos: Data for positive electrode OCV.
   :type df_pos: pd.DataFrame
   :param df_cell: Data for full cell OCV and derivatives.
   :type df_cell: pd.DataFrame
   :param \*\*kwargs: Keyword arguments. Optional key/value pairs are below:

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
   :type \*\*kwargs: dict, optional

   :raises ValueError: Invalid keyword arguments.

   .. rubric:: Notes

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


   .. py:method:: coarse_search(Nx)

      Determine the minimum error by evaluating parameter sets taken from
      intersections of a coarse grid. Parameter sets where x0 < x100 for
      either electrode are ignored.

      :param Nx: Number of discretizations between [0, 1] for each parameter.
      :type Nx: int

      :returns: **summary** (*dict*) -- Summarized results from the coarse search.



   .. py:method:: constrained_fit(x0)

      Run a trust-constrained local optimization routine to minimize error
      between the fit and data.

      :param x0: Initial x0_neg, x100_neg, x0_pos, x100_pos, and optionally iR.
      :type x0: ArrayLike, shape(n,)

      :returns: **summary** (*dict*) -- Summarized results from the optimization routine.



   .. py:method:: err_func(params)

      The cost function for coarse_search and constrained_fit.

      :param params: Array for x0_neg, x100_neg, x0_pos, x100_pos, and optionally iR.
      :type params: ArrayLike, shape(n,)

      :returns: **err_tot** (*float*) -- Total error based on a combination of cost_terms.



   .. py:method:: err_terms(params, full_output = False)

      Calculate error between the fit and data.

      :param params: Array for x0_neg, x100_neg, x0_pos, x100_pos, and iR (optional).
      :type params: ArrayLike, shape(n,)
      :param full_output: Flag to return all data. The default is False.
      :type full_output: bool, optional

      :returns: * **errs** (*tuple[float]*) -- If full_output is False, return voltage error, dqdv error, and
                  dvdq error values.
                * **full_output** (*dict*) -- If full_output is True, return a dictionary with the fit arrays,
                  data arrays, and error values.

      .. rubric:: Notes

      Error terms are the mean absolute errors between data and predicted
      values, normalized by the data. The normalization reduces preferences
      to fit any one cost term over others when more than one is considered.
      In addition, normalizing allows the errors to be added when the cost
      function includes more than one term.



   .. py:method:: ocv_spline(df, name)

      Generate OCV interpolation functions.

      :param df: Data with 'soc' and 'voltage' columns. If name is 'cell', the
                 data should also include 'dsoc_dV' and 'dV_dsoc' columnes.
      :type df: pd.DataFrame
      :param name: Dataset name, from {'neg', 'pos', 'cell'}.
      :type name: str

      :returns: * **ocv** (*callable*) -- If name is not 'cell' return a makima interpolation for OCV.
                * **ocv, dqdv, dvdq** (*tuple[callable]*) -- If name is 'cell', return a makima interpolation for OCV, dqdv,
                  and dvdq.



   .. py:method:: plot(params, **kwargs)

      Plot the fit vs. data.

      :param params: Parameters x0_neg, x100_neg, x0_pos, x100_pos, and optionally iR.
      :type params: ArrayLike, shape(n,)
      :param \*\*kwargs: Keyword arguments. Optional key/value pairs are below:

                         ============== ============================================
                         Key            Value (*type*, default)
                         ============== ============================================
                         fig            1x3 subplot figure to fill (*object*, None)
                         voltage_ylims  ylimits for voltage (*list[float]*, None)
                         dqdv_ylims     ylimits for dsoc_dV (*list[float]*, None)
                         dvdq_ylims     ylimits for dV_dsoc (*list[float]*, None)
                         ============== ============================================
      :type \*\*kwargs: dict, optional

      :returns: *None.*



   .. py:property:: bounds
      :type: list[float]

      Get or set the bounds for the constrained fit routine.


   .. py:property:: cost_terms
      :type: list[str]

      Get or set which terms are included in the constrained fit's cost
      function. Options are 'voltage', 'dqdv', and/or 'dvdq'.


   .. py:property:: df_cell
      :type: pandas.DataFrame

      Get or set the full cell dataframe.

      Columns must include 'soc' for state of charge, 'voltage' for the cell
      voltage, 'dsoc_dV' for the derivative dsov/dV, and 'dV_dsoc' for the
      derivative dV/dsoc. 'soc' should be normalized to [0, 1].


   .. py:property:: df_neg
      :type: pandas.DataFrame

      Get or set the negative electrode dataframe.

      Columns must include both 'soc' for state of charge and 'voltage' for
      the half-cell voltage. 'soc' should be normalized to [0, 1].


   .. py:property:: df_pos
      :type: pandas.DataFrame

      Get or set the positive electrode dataframe.

      Columns must include both 'soc' for state of charge and 'voltage' for
      the half-cell voltage. 'soc' should be normalized to [0, 1].


   .. py:property:: figure_font
      :type: int

      Get or set the figure fontsize.


   .. py:property:: maxiter
      :type: int

      Get or set the maximum iterations for the constrained fit routine.


   .. py:property:: smoothing
      :type: int

      Get or set the fit smoothing.

      The fitted dsoc/dV and dV/dsoc curves often have a lot of noise in
      them because they carry noise over from both half-cell OCV curves.
      This property is used to smooth the fitted derivatives. The smoothed
      curves are used to determine error between the fit and data.


   .. py:property:: xtol
      :type: float

      Get or set the 'x' tolerance for the constrained fit routine.


.. py:function:: clean_df(df, unique_cols = [], sort_by = None)

   Clean up dataframes for dqdv analysis.

   Drop all nan values, ensure specified columns do not have duplicates,
   and sort the whole dataframe according to a given column.

   :param df: A pandas dataframe.
   :type df: pd.DataFrame
   :param unique_cols: Columns to remove duplicate values, if present. The default is [].
   :type unique_cols: list[str], optional
   :param sort_by: Column name used to sort dataframe. The default is None.
   :type sort_by: str, optional

   :returns: **df** (*pd.DataFrame*) -- Cleaned and sorted dataframe.


.. py:function:: post_process(capacity, x)

   Determine degradation parameters.

   Uses full cell capacity and fitted x0/x100 values from dqdv/dvdq fits to
   calculate theoretical electrode capacities, loss of active material (LAM),
   and total inventory losses (TIL). TIL is used instead of LLI (loss of
   lithium inventory) because this analysis is also valid for intercalation
   electrodes with active species other than lithium.

   Electrode capacities (Q) and losses of active material (LAM) are

   .. math::

       Q_{ed} = \frac{\rm capacity}{x_{100,ed} - x_{0,ed}}, \quad \quad
       {\rm LAM}_{ed} = 1 - \frac{Q_{ed}}{Q_{ed}[0]},

   where :math:`ed` is used generically 'electrode'. In the output, subscripts
   'neg' and 'pos' are used to differentiate between the negative and positive
   electrodes, respectively. Loss of inventory is

   .. math::

       I = x_{100,neg}Q_{neg} + x_{100,pos}Q_{pos}, \quad \quad
       {\rm TIL} = 1 - \frac{I}{I[0]},

   where :math:`I` is an array of inventories calculated from the capacities
   :math:`Q` above. The 'offset' output can also sometimes serve as a helpful
   metric. It is simply the difference between 'x0_neg' and 'x0_pos'.

   :param capacity: Full cell capacity values per fitted profile.
   :type capacity: ArrayLike, shape(n,)
   :param x: Fitted x0/x100 values. Row i corresponds to capacity[i], with column
             order: x0_neg, x100_neg, x0_pos, x100_pos.
   :type x: ArrayLike, shape(n,4)

   :raises ValueError: capacity.size != x.shape[0].
   :raises ValueError: x.shape[1] != 4.

   :returns: **results** (*dict*) -- Electrode capacities (Q) and loss of active material (LAM) for the
             negative (neg) and positive (pos) electrodes, and total loss of
             intentory (TLI). Capacity units match the ``capacity`` input. All
             other outputs are unitless.


.. py:function:: run_gui()

   Run a graphical interface for the Fitter class.

   :returns: *None.*


