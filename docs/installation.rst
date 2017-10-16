.. include:: references.txt

.. _install:

************
Installation
************

The **hips** package works with Python 3.6 or later, on Linux, MacOS and Windows.

Installing the latest stable version is possible either using pip or conda.

How to install the latest development version is desribed on the :ref:`develop` page.

Using pip
=========

To install hips with `pip <http://www.pip-installer.org/en/latest/>`_
from `PyPI <https://pypi.python.org/pypi/hips>`_, run::

    pip install hips --no-deps

.. note::

    The ``--no-deps`` flag is optional, but highly recommended if you already
    have Numpy installed, since otherwise pip will sometimes try to "help" you
    by upgrading your Numpy installation, which may not always be desired.

Using conda
===========

To install hips with `Anaconda <https://www.continuum.io/downloads>`_
from the `conda-forge channel on anaconda.org <https://anaconda.org/conda-forge/hips>`__
simply run::

    conda install -c conda-forge hips

Check installation
==================

To check if you have ``hips`` installed, where it was installed and which version you have:

.. code-block:: bash

    $ python
    >>> import hips  # doctest: +SKIP
    >>> hips.__version__  # doctest: +SKIP
    # -> prints which version you have
    >>> hips  # doctest: +SKIP
    # -> prints where hips is installed

To see if you have the latest stable, released version of ``hips``, you can find that version here:

* https://pypi.python.org/pypi/hips
* https://anaconda.org/conda-forge/hips

Next you could try running the examples at :ref:`gs` and see if you get the expected output.

It's usually not necessary, but if you find that your ``hips`` installation gives errors
or unexpected results for examples that should work, you can run the ``hips`` automated tests via:

.. code-block:: bash

    python -c 'import hips; hips.test()'

For more information on automated tests, see the :ref:`develop` page.

Dependencies
============

The ``hips`` package has the following requirements:

* Python 3.6 or later!
* `Numpy`_ 1.11 or later
* `Astropy`_ 1.2 or later
* `astropy-healpix`_ 0.2 or later
* `scikit-image`_ 0.12 or later. (Older versions could work, but aren't tested.)
* `Pillow`_ 4.0 or later. (Older versions could work, but aren't tested.)
  Pillow is the friendly Python Imaging Library (``PIL``) fork, for JPEG and PNG tile I/O.

In addition, the following packages are needed for optional functionality:

* `Matplotlib`_ 2.0 or later. Used for plotting in examples.
* `tqdm`_. Used for showing progress bar either on terminal or in Jupyter notebook.
* `aiohttp`_. Used for fetching HiPS tiles.

We have some info at :ref:`py3` on why we don't support legacy Python (Python 2).