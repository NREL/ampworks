import pandas as pd
import ampworks as amp
from scipy._lib._util import _RichResult  # Used to make printing pretty

# Import the data
# ===============
# The negative electrode dataframe (df_neg) and positive electrode dataframe
# (df_pos) must have columns 'soc' and 'voltage'. The full cell dataframe needs
# 'soc', 'voltage', 'dsoc_dV', and 'dV_dsoc' columns. 

# An important note: The fitting routine assumes all dataframe 'soc' columns
# are in the reference direction of the full cell. Therefore, the negative
# electrode voltage should decrease as 'soc' increases whereas the positive
# electrode and full cell voltages should increse as their 'soc' increase.

df_neg = pd.read_csv('an_T23_C_24_dis.csv')  # negative electrode data
df_pos = pd.read_csv('ca_T23_C_6_ch.csv')    # positive electrode data

df_cell_BOL = pd.read_csv('charge2.csv')     # full cell at beginning of life
df_cell_EOL = pd.read_csv('charge3866.csv')  # full cell at end of life

# Create a fitter instance
# ========================
# The fitter class is used to hold and fit the data. There are a few keyword
# arguments you can see by running help(amp.dqdv.Fitter). Mostly the defaults
# are good, but you might want to change 'cost_terms' to include 'voltage' so
# that an iR offset is fit in addition to the xmin/xmax values of the two
# electrodes. 

# Any keyword argument can also be changed after initializing the instance, as
# shown below. 

fitter = amp.dqdv.Fitter(df_neg, df_pos, df_cell_BOL)
fitter.cost_terms = ['voltage', 'dqdv', 'dvdq']

# Coarse searches
# ===============
# Because fitting routines can get stuck in local minima, it can be important
# to have a good initial guess. The 'coarse_search()' method helps with this.
# Given a number of discretizations, it applies a brute force method to find
# a good initial guess by discretizing the xmin/xmax regions into Nx points,
# and evaluating all physically realistic locations (i.e., xmax > xmin). The
# result isn't always great, but is typically good enough to use as a starting
# value for a more robust fitting routine.

# The output from all 'fits' (coarse searches or otherwise) are dictionaries.
# You can format the dictionary so that it prints well by using the _RichResult
# class from scipy, as shown below. You can also see what the plot of the best
# fit looks like using the 'plot()' method, which takes in the fit results.

summary1 = fitter.coarse_search(11)
print(_RichResult(**summary1), "\n")
fitter.plot(summary1['x'])

# Constrained fits
# ================
# The 'constrained_fit()' method executes a routine from scipy.optimize to find
# values of xmin/xmax (and and iR offset if 'voltage' is in 'cost_terms'). The
# routine forces xmax > xmin for each electrode and sets bounds (+/-) on each
# xmin and xmax based on the 'fitter.bounds' attributes. See the docstrings for
# more information and detail.

# The 'constrained_fit()' method takes in a starting guess. You can pass the
# summary from the 'coarse_search()' if you ran one. Otherwise, you can start
# with the 'constrained_fit()' routine right way and pass the output from a
# previous routine back in to see if the fit continues to improve.

summary2 = fitter.constrained_fit(summary1['x'])
print(_RichResult(**summary2), "\n")
fitter.plot(summary2['x'])

# Swapping to another data set
# ============================
# There is no need to create a 'fitter' instance for multiple files if you are
# batch processing data. Instead, fit the full cell data starting at beggining
# of life (BOL) and moving toward end of life (EOL). A guess from the previous
# previous best fit is typically good enough that there is no need to re-run a
# 'coarse_search()' routine.

fitter.df_cell = df_cell_EOL

summary3 = fitter.constrained_fit(summary2['x'])
print(_RichResult(**summary3), "\n")
fitter.plot(summary3['x'])

# Using a GUI
# ===========
# You can run the following command to launch a GUI to do the fits one at a
# time, manually. It is relatively straight forward to understand and use, but
# is not indendend for batch processing, so is slow if you have many curves to
# fit.

# amp.dqdv.run_gui()
