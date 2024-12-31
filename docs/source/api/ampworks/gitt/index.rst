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

   :param thick: Electrode thickness [m].
   :type thick: float
   :param area: Cell area (e.g., pi*R**2 for coin cells) [m2].
   :type area: float
   :param eps_el: Electrolyte/pore volume fraction [-].
   :type eps_el: float
   :param eps_CBD: Carbon-binder-domain volume fraction [-]. See notes for more info.
   :type eps_CBD: float
   :param Rp_AM: Active material particle radius [m].
   :type Rp_AM: float
   :param rho_AM: Active material mass density [kg/m3].
   :type rho_AM: float
   :param mass_AM: Total active material mass [kg].
   :type mass_AM: float
   :param MW_AM: Active material molecular weight [kg/kmol].
   :type MW_AM: float

   :returns: *None.*

   .. rubric:: Notes


   .. py:property:: As_AM
      :type: float


      Total active material surface area [m2].


   .. py:property:: Vm_AM
      :type: float


      Electrode volume [m3].


   .. py:property:: capacity
      :type: float


      Electrode volume [m3].


   .. py:property:: eps_AM
      :type: float


      Active material volume fraction [-].


   .. py:property:: volume
      :type: float


      Electrode volume [m3].


.. py:class:: GITTDataset(time, current, voltage, avg_temperature, invert_current = False)

   GITT dataclass wrapper

   :param time: Recorded test times [s].
   :type time: 1D np.array
   :param current: Timeseries current data [A].
   :type current: 1D np.array
   :param voltage: Timeseries voltage data [V].
   :type voltage: 1D np.array
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


