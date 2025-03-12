# ampworks

## Summary
`ampworks` is a collection of tools designed to process experimental battery data with a focus on model-relevant analyses. It currently provides functions for incremental capacity analysis and GITT data processing, helping extract key properties for life and physics-based models (e.g., SPM and P2D). Some tools, like the incremental capacity analysis module, also include graphical user interfaces for ease of use.

This software is in early development (Alpha), and the API may change as it matures.

## Installation
`ampworks` can be installed from [PyPI](https://pypi.org/project/ampworks) use the following command.

```
pip install ampworks[gui]
```

Using `[gui]` is optional. When included, the installation will setup optional dependencies that are needed for the optional graphical user interfaces (GUIs). However, the package is designed such that there are no features that specifically require the GUIs. Without the optional dependencies the package takes up less space on your computer, and will generally install faster.

For those interested in setting up a developer and/or editable version of this software please see the directions available in the "Development" section of our [documentation](https://ampworks.readthedocs.io/en/latest/development).

## Get Started
The best way to get started is by exploring the `examples` folder, which includes real datasets and demonstrates key functionality. These examples will evolve as the software progresses.

**Notes:**
* If you are new to Python, check out [Spyder IDE](https://www.spyder-ide.org/). Spyder is a powerful interactive development environment (IDE) that can make programming in Python more approachable to new users.
* Another friendly option for getting started in Python is to use [Jupyter Notebooks](https://jupyter.org/). We write our examples in Jupyter Notebooks since they support both markdown blocks for explanations and executable code blocks.
* Python, Spyder, and Jupyter Notebooks can be setup using [Anaconda](https://www.anaconda.com/download/success). Anaconda provides a convenient way for new users to get started with Python due to its friendly graphical installer and environment manager.

## Citing this Work
This work was authored by researchers at the National Renewable Energy Laboratory (NREL). If you use use this package in your work, please include the following citation:

> Randall, Corey R. "ampworks: Battery data analysis tools in Python [SWR-25-39]." Computer software. url: https://github.com/NREL/ampworks. doi: (awaiting doi).

For convenience, we also provide the following for your BibTex:

```
@misc{Randall-2024,
  title = {{ampworks: Battery data analysis tools in Python [SWR-25-39]}},
  author = {Randall, Corey R.},
  doi = {awaiting doi},
  url = {https://github.com/NREL/ampworks},
  year = {2025},
}
```

## Contributing
If you'd like to contribute to this package, please look through the existing [issues](https://github.com/NREL/ampworks/issues). If the bug you've caught or the feature you'd like to add isn't already being worked on, please submit a new issue before getting started. You should also read through the [developer guidelines](https://ampworks.readthedocs.io/en/latest/development).

## Disclaimer
This work was authored by the National Renewable Energy Laboratory (NREL), operated by Alliance for Sustainable Energy, LLC, for the U.S. Department of Energy (DOE). The views expressed in the repository do not necessarily represent the views of the DOE or the U.S. Government.
