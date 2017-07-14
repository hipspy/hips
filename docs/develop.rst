.. include:: references.txt

.. _develop:

*******
Develop
*******

Hello!
======

Want to contribute to the ``hips`` package?

Great! Talk to us by filing a Github issue any time
(it doesn't have to be a concrete feature request or bug report).

This package was created using the Astropy affiliated package template,
and everything works pretty much as in Astropy and most affiliated packages.

We didn't write any developer docs specifically for this package yet.
For now, check out the Astropy core package developer docs,
or just talk to us if you have any questions.

Install development version
===========================

Install the latest development version from https://github.com/hipspy/hips :

.. code-block:: bash

    git clone https://github.com/hipspy/hips
    cd hips
    pip install .

Then run the tests with either of these commands:

.. code-block:: bash

    python -m pytest -v hips
    python setup.py test -V

To run all tests and get a coverage report:

.. code-block:: bash

    python setup.py test -V --remote-data --coverage

To build the documentation, do:

.. code-block:: bash

    python setup.py build_docs

Get the hips-extra test datasets
================================

To run tests accessing files from `hips-extra <https://github.com/hipspy/hips-extra>`_
repository, users must have it cloned on their system, otherwise some test cases
will be skipped. This contains tiles from different HiPS surveys which are used
by the drawing module. After this, the ``HIPS_EXTRA`` environment variable must
be set up on their system. On UNIX operating systems, this can be set using

.. code-block:: bash

    export HIPS_EXTRA=path/to/hips-extra

.. _py3:

Why only Python 3?
==================

This package requires Python 3.6 or later.

It will not work with Python 2.7 or 3.5!

This was a choice we made when starting this package in summer of 2017, at a time
when Jupyter had just made their Python 3 only release and other packages we depend
on (like Astropy) were about to drop support for legacy Python (Python 2).

Supporting only Python 3 means we e.g. get these benefits:

* async / await for asynchronous HiPS tile fetching (introduced in Python 3.5)
* Keyword-only arguments (introduced in Python 3.0)
* Type annotations (some only introduced in Python 3.6)
* f-strings (introduced in Python 3.6)

At the moment, the only Python 3.6 only feature we use are f-strings, so if several
potential users that are on Python 3.5 and can't easily upgrade for some reason
complain, we might consider supporting Python 3.5 in the next release.

