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
   :param invert_current: Inverts signs for 'current' values. Charge/discharge currents
                          should be positive/negative, respectively. The default is False.
   :type invert_current: bool, optional

   :returns: *None.*

   :raises ValueError: 'time' array must be increasing.


.. py:function:: extract_params(flag, cell, data, return_stats = False, **options)

   _summary_

   :param flag: _description_
   :type flag: int
   :param cell: _description_
   :type cell: CellDescription
   :param data: _description_
   :type data: GITTDataset
   :param return_stats: _description_, by default False
   :type return_stats: bool, optional

   :returns: *pd.DataFrame* -- _description_

   :raises ValueError: _description_


