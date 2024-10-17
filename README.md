## Installation
To install, download the repository files onto your local machine, or clone the repo:
```
git clone https://github.com/NREL/ampworks.git
```

``ampworks`` only supports Python versions 3.9 through 3.13. Make sure one of these is installed on your computer. If you are new to Python, we recommend download and using [Anaconda](https://anaconda.com/download/success) to get started.

With a supported Python version installed and the repo files available on your local machine, use your terminal to navigate into the repo folder, and run the command below to install ``ampworks``.
```
pip install .
```
If you plan to make changes to the source code, we also support editable installations. When installed in editable mode, any changes you make to the source code are immediately reflected in your installed package. We recommend including the optional developer dependencies when installing in editable mode. To install with these configurations, run the following code instead of the one above.
```
pip install -e .[dev]
```