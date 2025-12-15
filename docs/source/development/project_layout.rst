Project Layout
==============
The `ampworks` project is organized to provide clarity and structure, making it easy for developers to navigate and contribute. Below is an outline of the key directories and files, along with guidelines for working within them.

Root Directory
--------------
The root directory contains the most important files and folders necessary for development:

* **src/:** The core package code resides in this directory. This is the primary folder developers will interact with when modifying or adding features.
* **pyproject.toml:** This file contains the project's build system configurations and dependencies. If you need to add or modify dependencies, you should do so in this file.
* **noxfile.py:** Contains automation scripts for tasks like testing, linting, formatting, and building documentation. Developers should use nox sessions as needed to ensure code quality and consistency.
* **tests/:** This is where all unit tests and integration tests are stored. Any new functionality should include appropriate tests here.
* **docs/:** Contains documentation files for the project. Developers contributing to the documentation should work here, particularly if adding or improving developer guides or API references.

Source Directory
----------------
The `src/` directory contains the main package code. Using this structure ensures that local imports during development come from the installed package rather than accidental imports from the source files themselves.

Package Structure
^^^^^^^^^^^^^^^^^
Sub-modules/subpackages of the `ampworks` package reside at the top level of the `src/` directory and include, for example:

* `_core`: Core reading, writing, and container classes. In particular, most functions build of the `Dataset` class, which is a custom subclass of `pd.DataFrame`.
* `datasets`: Functions to load, print, and download example datasets for testing and demonstration purposes.
* `dqdv`: Methods to help with differential analysis. For example, extract aging parameters through an incremental capacity analysis.
* `gitt`: Analysis tools for galvanostatic intermittent titration test data. Extracts kinetic and transport properties for numerical models.

Note that this list is not exhaustive. Organization within each subpackage is designed such that classes typically resides in their own file, following a philosophy of keeping files manageable in size. If multiple classes or functions share significant overlap in purpose, they may be grouped in the same file, but care is taken to keep files concise and easy to navigate.
