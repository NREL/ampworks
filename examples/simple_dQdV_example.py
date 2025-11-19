import pandas as pd
import ampworks as amp

# Import the data
# ===============
# Preprocess your data such that you have a representation of the negative and
# positive electrodes, and full cell potentials in dataframes. All dataframes
# require columns labeled 'soc' and 'voltage', where 'soc' has already been
# normalized to be between zero and one.

# An important note: The fitting routine assumes all dataframe 'soc' columns
# are in the reference direction of the full cell. Therefore, the negative
# electrode voltage should decrease as 'soc' increases whereas the positive
# electrode and full cell voltages should increase as their 'soc' increase.

neg = pd.read_csv('gr.csv')   # negative electrode data
pos = pd.read_csv('nmc.csv')  # positive electrode data

cell_BOL = pd.read_csv('charge2.csv')     # full cell at beginning of life
cell_EOL = pd.read_csv('charge3866.csv')  # full cell at end of life

# Create a fitter instance
# ========================
# The fitter class is used to hold and fit the data. Aside from inputing the
# electrode and full cell data you can choose how you'd like the optimization
# to run by setting 'cost_terms'. By default, the objective function minimizes
# errors across voltage, dqdv, and dvdq simultaneously. However, you can also
# choose to minimize based on any subset of these three. Note that 'cost_terms'
# can also be changed after initialization, as shown below. The datasets can
# also be replaced by re-setting any of the 'neg', 'pos', or 'cell' properties.

fitter = amp.dqdv.DqdvFitter(neg, pos, cell_BOL)
fitter.cost_terms = ['voltage', 'dqdv', 'dvdq']

# Grid searches
# =============
# Because fitting routines can get stuck in local minima, it can be important
# to have a good initial guess. The 'grid_search()' method helps with this.
# Given a number of discretizations, it applies a brute force method to find
# a good initial guess by discretizing the xmin/xmax regions into Nx points,
# and evaluating all physically realistic locations (i.e., xmax > xmin). The
# result isn't always great, but is typically good enough to use as a starting
# value for a more robust fitting routine. You can also see what the plot of
# the best fit looks like using the 'plot()' method, which takes a fit result.

fitres1 = fitter.grid_search(11)
fitter.plot(fitres1.x)
print(fitres1, "\n")

# Constrained fits
# ================
# The 'constrained_fit()' method executes a routine from scipy.optimize to find
# values of xmin/xmax (and and iR offset if 'voltage' is in 'cost_terms'). The
# routine forces xmax > xmin for each electrode and sets bounds (+/-) on each
# xmin and xmax based on the 'bounds' keyword argument. See the docstrings for
# more information and detail on changing some of the optimization options.

# The 'constrained_fit()' method takes in a starting guess. You can pass the
# fit result from the 'grid_search()' if you ran one. Otherwise, you can start
# with the 'constrained_fit()' routine right way and pass the output from a
# previous routine back in to see if the fit continues to improve.

fitres2 = fitter.constrained_fit(fitres1.x)
fitter.plot(fitres2.x)
print(fitres2, "\n")

# Swapping to another data set
# ============================
# There is no need to create a 'fitter' instance for multiple files if you are
# batch processing data. Instead, fit the full cell data starting at beginning
# of life (BOL) and move toward end of life (EOL). A guess from the previous
# fit is typically good enough that there is no need to re-run 'grid_search()'.

fitter.cell = cell_EOL

fitres3 = fitter.constrained_fit(fitres2.x)
fitter.plot(fitres3.x)
print(fitres3, "\n")

# Calculating LAM/LLI
# ===================
# If your main purpose for the dQdV fitting is to calculate loss of active
# material (LAM) and loss of lithium inventory (LLI) then you will need to
# loop over and collect the fitted stoichiometries from many cell datasets
# throughout life. Use 'DqdvFitTable' to store all of your results. Then call
# 'calc_lam_lli' and 'plot_lam_lli' to calculate and/or visualize degradation
# modes. Simply initialize an instance of 'DqdvFitTable' before you loop
# over all of your fits, and append the fit result to the table instance after
# each fit is completed. For example, below we make an instance and add the
# fitres2 and fitres3 results. The fitres1 result is skipped because it was
# only performed to give a better starting guess for the constrained fit that
# provided fitres2. 'DqdvFitTable' also allows you to track some of your
# own metrics as well via an 'extra_cols' argument. This can be used to have
# columns like 'days', 'efc', 'cycle_number', etc. that you might want to keep
# track of for plotting or fitting life models to later. This is not shown
# below, but info is available in the docstrings for interested users. You can
# access all of the results info via its 'df' property, which is just a standard
# pandas DataFrame. This gives you access to save the results, add columns in
# post-processing steps, etc.

results = amp.dqdv.DqdvFitTable()
results.append(fitres2)
results.append(fitres3)

results.plot_lam_lli()

# Using a GUI
# ===========
# If you installed ampworks with the optional GUI dependencies (either by using
# pip install ampworks[gui] or pip install .[dev]), then you can also perform
# this analysis using a local web interface. Simply execute the command below
# in your terminal (or Anaconda Prompt) to launch the GUI. It is relatively
# straight forward to use, however, the user guide is not yet available. This
# will be added in a future release as the software matures.

# ampworks --app dQdV

# If you are using Jupyter Notebooks you can also launch the GUI from any code
# cell using the following function. There are a couple inputs you can use to
# allow the GUI to run within Jupyter or to launch an external tab. You can
# also control the app height if you choose to run the GUI within a Jupyter
# cell.

# amp.dqdv.run_gui()
