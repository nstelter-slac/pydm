[![Build Status](https://github.com/slaclab/pydm/actions/workflows/run-tests.yml/badge.svg?branch=master)](https://github.com/slaclab/pydm/actions/workflows/run-tests.yml)

![PyDM: Python Display Manager](pydm_banner_full.png)

<p>
  <img src="pydm_launcher/icons/pydm_128.png" width="128" height="128" align="right"/>
  <h1>PyDM: Python Display Manager</h1>
</p>

<p align="left">
  PyDM is a PyQt-based framework for building user interfaces for control systems.
  The goal is to provide a no-code, drag-and-drop system to make simple screens,
  as well as a straightforward Python framework to build complex applications.
  <br>
  <br>
</p>
<p align="center">
  <strong>« Explore PyDM <a href="https://slaclab.github.io/pydm/">docs</a> and <a href="https://slaclab.github.io/pydm/tutorials/index.html">tutorials</a> »</strong>
  <br>
  <br>
  <a href="https://github.com/slaclab/pydm/issues/new?template=bug-report.yml">Report bug</a>
  ·
  <a href="https://github.com/slaclab/pydm/issues/new?template=feature-request.yml">Request feature</a>
  ·
  <a href="https://github.com/slaclab/pydm/blob/master/CONTRIBUTING.rst">How to Contribute</a>
  ·
  <a href="https://github.com/slaclab/pydm/blob/master/SUPPORT.md">Support</a>
</p>

<br>

# Requirements
* Python 3.9+
* Qt 5.6 or higher
* qtpy
* PyQt5 >= 5.7 or any other Qt Python wrapper.
> **Note:**
> If you'd like to use Qt Designer (drag-and-drop tool to build interfaces) you'll
> need to make sure you have the PyQt plugin for Designer installed.  This usually
> happens automatically when you install PyQt from source, but if you install it
> from a package manager, it may be left out.

Python package requirements are listed in the requirements.txt file, which can
be used to install all requirements from pip: 'pip install -r requirements.txt'

PyDM project uses the [qtpy](https://github.com/spyder-ide/qtpy)
as the abstraction layer for the Qt Python wrappers (PyQt5/PyQt4/PySide2/PySide).
**PyQt5 is currently the only supported Qt Python wrapper**.

# Installation

See the [installation docs](https://slaclab.github.io/pydm/installation.html#installing-pydm-and-prerequisites-with-conda) for instructions on how to setup an environment and install the latest PyDM build. Follow these setup instructions if you just wish to run the prebuilt PyDM executable.

# Developers

Developers should check out the [contributing docs](https://github.com/slaclab/pydm/blob/master/CONTRIBUTING.rst) for steps on getting set up for local PyDM development. Follow these setup instructions if you wish to modify and run the PyDM source code.

# PyDM Widgets in Designer
PyDM widgets are written in Python, and are loaded into QtDesigner via the PyQt Designer Plugin.

If you want to use the PyDM widgets in QtDesigner, add the /pydm directory
(which holds pydm_designer_plugin.py) to your PYQTDESIGNERPATH environment variable.
Eventually, this will happen automatically in some kind of setup script.

When Conda is used to install PyDM into a Linux Environment, it will automatically
define the PYQTDESIGNERPATH environment variable to point to the /etc/pydm dir containing pydm_designer_plugin.py.

For more information please see our <a href="https://slaclab.github.io/pydm/installation.html#designer-plugin-path">installation guide</a>.