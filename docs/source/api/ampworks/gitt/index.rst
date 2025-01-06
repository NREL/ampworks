ampworks.gitt
=============

.. py:module:: ampworks.gitt

.. autoapi-nested-parse::

   .. rubric:: TODO



Classes
-------

.. autoapisummary::

   ampworks.gitt.CellDescription
   ampworks.gitt.GITTDataset


Functions
---------

.. autoapisummary::

   ampworks.gitt.extract_params


Package Contents
----------------

.. py:class:: CellDescription

   Cell description wrapper

   :param thick_ed: Electrode thickness [m].
   :type thick_ed: float
   :param area_ed: Projected electrode area (e.g., pi*R**2 for coin cells, L*W for pouch
                   cells, etc.) [m2].
   :type area_ed: float
   :param eps_el: Electrolyte/pore volume fraction [-].
   :type eps_el: float
   :param eps_CBD: Carbon-binder-domain volume fraction [-]. See notes for more info.
   :type eps_CBD: float
   :param radius_AM: Active material particle radius [m].
   :type radius_AM: float
   :param rho_AM: Active material mass density [kg/m3].
   :type rho_AM: float
   :param mass_AM: Total active material mass [kg].
   :type mass_AM: float
   :param molar_mass_AM: Active material molar mass [kg/kmol].
   :type molar_mass_AM: float

   :returns: *None.*

   .. rubric:: Notes

   A "convenient" way to get ``eps_CBD`` requires knowledge of the densities
   and masses for all solid phases in your slurry (carbon additive, binder,
   and active material). The volume fraction for any phase :math:`m` is

   .. math::

       \varepsilon_{m} = f_{m} \varepsilon_{\rm s},

   where :math:`f_{m}` is the volume of phase :math:`m` per volume of solid
   phase and :math:`\varepsilon_{\rm s} = 1 - \varepsilon_{\rm el}` is
   the total solid-phase volume fraction. :math:`f_{m}` is calculated as

   .. math::

       f_{m} = \frac{m_{m} / \rho_{m}}{\sum_{i=1}^{N} m_{i} / \rho_{i}},

   Here, the numerator uses the mass and density of phase :math:`m` to get
   its individual volume, and the denominator sums over all :math:`N` solid
   phases to calculate the total solid-phase volume. Using these expressions,
   you can separately calculate volume fractions for the carbon additive and
   binder. Finally, adding their values together gives

   .. math::

       \varepsilon_{\rm CBD} = \varepsilon_{\rm C}
                               + \varepsilon_{\rm B}.


   .. py:property:: eps_AM
      :type: float

      Active material volume fraction [-].


   .. py:property:: molar_vol_AM
      :type: float

      Active material molar volume [m3/kmol].


   .. py:property:: spec_capacity_AM
      :type: float

      Theoretical specific capacity [Ah/kg].


   .. py:property:: surf_area_AM
      :type: float

      Total active material surface area [m2].


   .. py:property:: volume_ed
      :type: float

      Electrode volume [m3].


.. py:class:: GITTDataset(time, current, voltage, avg_temperature, invert_current = False)

   GITT dataclass wrapper

   :param time: Recorded test times [s].
   :type time: ArrayLike, shape(n,)
   :param current: Timeseries current data [A].
   :type current: ArrayLike, shape(n,)
   :param voltage: Timeseries voltage data [V].
   :type voltage: ArrayLike, shape(n,)
   :param avg_temperature: Average temperature of the experiment [K].
   :type avg_temperature: float
   :param invert_current: Inverts the 'current' sign values. Charge and discharge currents
                          should be positive and negative, respectively. Defaults to False.
   :type invert_current: bool, optional

   :returns: *None.*

   :raises ValueError: 'time' array must be increasing.


   .. py:method:: find_pulses(pulse_sign, plot = False)

      Finds the indices in the data where pulses start and end. The algorithm
      depends on there being a rest period both before and after each pulse.

      :param pulse_sign: The sign of the current pulses to find. Use `+1` or `-1` for
                         positive and negative pulses, respectively.
      :type pulse_sign: int
      :param plot: Whether or not to plot the result. The default is False.
      :type plot: bool, optional

      :returns: * **start** (*int*) -- Indices where pulse starts were detected.
                * **stop** (*int*) -- Indices where pulse stops were detected.

      :raises ValueError: Size mismatch: The number of detected pulse starts and stops do
          not agree. This typically occurs due to a missing rest. You will
          likely need to manually remove affected pulse(s).



.. py:function:: extract_params(pulse_sign, cell, data, return_stats = False, **options)

   _summary_

   :param pulse_sign: The sign of the current pulses to process. Use `+1` for positive pulses
                      and `-1` for negative pulses.
   :type pulse_sign: int
   :param cell: Description of the cell.
   :type cell: CellDescription
   :param data: The GITT data to process.
   :type data: GITTDataset
   :param return_stats: Adds a second return value with some statistics from the experiment,
                        see below. The default is False.
   :type return_stats: bool, optional
   :param \*\*options: Keyword options to further control the function behavior. A full list
                       of names, types, descriptions, and defaults is given below.
   :type \*\*options: dict, optional
   :param R2_lim: Lower limit for the coefficient of determination. Pulses whose linear
                  regression for `sqrt(time)` vs `voltage` that are less than this value
                  result in a diffusivity of `nan`. The default is 0.95.
   :type R2_lim: float, optional
   :param replace_nans: If True (default) this uses interpolation to replace `nan` diffusivity
                        values. When False, `nan` values will persist into the output.
   :type replace_nans: bool, optional

   :returns: * **params** (*dict*) -- A dictionary of the extracted parameters from each pulse. The keys are
               `xs [-]` for the intercalation fractions, `Ds [m2/s]` for diffusivity,
               `i0 [A/m2]` for exchange current density, and `OCV [V]` for the OCV.
             * **stats** (*dict*) -- Only returned when 'return_stats' is True. Provides key/value pairs for
               the number of pulses, average pulse current, and average rest and pulse
               times.

   :raises ValueError: 'options' contains invalid key/value pairs.


