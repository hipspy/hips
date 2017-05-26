.. include:: references.txt

.. _install:

************
Installation
************

.. warning::

    This ``hips`` package is in a very early stage of development.
    We started to work on it in June 2017 and expect to have a first v0.1 release in summer 2017.

    The instructions below will only become accurate once we make a first release.
    For now, please use the development version!


The ``hips`` package has the following requirements:

* Python 3.6 or later!
* `Numpy`_ 1.11 or later
* `Astropy`_ 1.2 or later
* `Healpy`_ 1.10 or later

In addition, the following packages are needed for optional functionality:

* `Matplotlib`_ 2.0 or later

.. note::

    This package requires Python 3.6 or later. It will not work with Python 2.7 or 3.5!

    Feature or pull requests asking to support older Python versions will be closed.
    We discussed this point and made an intentional decision to use modern Python features to implement this package.

    E.g. we use the following Python features (very incomplete list):

    * async / await for asynchronous HiPS tile fetching (introduced in Python 3.5)
    * Keyword-only arguments (introduced in Python 3.0)
    * f-strings (introduced in Python 3.6)
    * Type annotations (some only introduced in Python 3.6)

Stable version
==============

Installing the latest stable version is possible either using pip or conda.

Using pip
---------

To install hips with `pip <http://www.pip-installer.org/en/latest/>`_
from `PyPI <https://pypi.python.org/pypi/hips>`_, run::

    pip install hips --no-deps

.. note::

    The ``--no-deps`` flag is optional, but highly recommended if you already
    have Numpy installed, since otherwise pip will sometimes try to "help" you
    by upgrading your Numpy installation, which may not always be desired.

Using conda
-----------

To install hips with `Anaconda <https://www.continuum.io/downloads>`_
from the `astropy channel on anaconda.org <https://anaconda.org/astropy/hips>`__
simply run::

    conda install -c astropy hips

Testing installation
--------------------

To check if there are any issues with your installation, you can run the tests:

.. code-block:: bash

    python -c 'import hips; hips.test()'

Development version
===================

Install the latest development version from https://github.com/hipspy/hips :

.. code-block:: bash

    git clone https://github.com/hipspy/hips
    cd hips
    pip install .

Then run the tests with either of these commands:

.. code-block:: bash

    python -m pytest hips
    python setup.py test


To build the documentation, do:

.. code-block:: bash

    python setup.py build_docs
