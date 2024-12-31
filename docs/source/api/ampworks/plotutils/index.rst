ampworks.plotutils
==================

.. py:module:: ampworks.plotutils

.. autoapi-nested-parse::

   .. rubric:: TODO



Functions
---------

.. autoapisummary::

   ampworks.plotutils.add_text
   ampworks.plotutils.cb_line_plot
   ampworks.plotutils.format_ticks
   ampworks.plotutils.reset_rcparams
   ampworks.plotutils.set_font_rcparams
   ampworks.plotutils.set_tick_rcparams


Package Contents
----------------

.. py:function:: add_text(ax, xloc, yloc, text)

   Adds text to ``ax`` at a specified location.

   :param ax: An ``axis`` instance from a ``matplotlib`` figure.
   :type ax: object
   :param xloc: Relative location (0-1) for text start in x-direction.
   :type xloc: float
   :param yloc: Relative location (0-1) for text start in y-direction.
   :type yloc: float
   :param text: Text string to add to figure.
   :type text: str

   :returns: *None.*


.. py:function:: cb_line_plot(ax, xdata, ydata, zdata, cmap = 'jet', **kwargs)

   TODO

   :param ax: _description_
   :type ax: object
   :param xdata: _description_
   :type xdata: list[_ndarray]
   :param ydata: _description_
   :type ydata: list[_ndarray]
   :param zdata: _description_
   :type zdata: _ndarray
   :param cmap: _description_, by default 'jet'
   :type cmap: str, optional

   :raises ValueError: _description_


.. py:function:: format_ticks(ax, xdiv = None, ydiv = None)

   Formats ``ax`` ticks.

   Top and right ticks are turned on, tick direction is set to 'in', and
   minor ticks are made visible with the specified number of subdivisions.

   :param ax: An ``axis`` instance from a ``matplotlib`` figure.
   :type ax: object
   :param xdiv: Number of divisions between x major ticks. The default is None, which
                performs an 'auto' subdivision.
   :type xdiv: int, optional
   :param ydiv: Number of divisions between y major ticks. The default is None, which
                performs an 'auto' subdivision.
   :type ydiv: int, optional

   :returns: *None.*


.. py:function:: reset_rcparams()

   Sets ``plt.rcParams`` back to defaults.

   :returns: *None.*


.. py:function:: set_font_rcparams(fontsize = 10, family = 'sans-serif')

   Sets ``plt.rcParams`` font details.

   :param fontsize: Font size to use across all figures. The default is 10.
   :type fontsize: int, optional
   :param family: Font family from {'serif', 'sans-serif'}. The default is 'sans-serif'.
   :type family: str, optional

   :returns: *None.*


.. py:function:: set_tick_rcparams(allsides = True, minorticks = True, direction = 'in')

   Sets ``plt.rcParams`` tick details.

   :param allsides: Turns on ticks for top and right sides. The default is True.
   :type allsides: bool, optional
   :param minorticks: Makes minor ticks visible. The default is True.
   :type minorticks: bool, optional
   :param direction: Tick direction from {'in', 'out'}. The default is 'in'.
   :type direction: str, optional

   :returns: *None.*


