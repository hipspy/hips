.. include:: references.txt

.. _hipsgen:

*************
Generate HiPS
*************

The `~hips.healpix_to_hips` function can be used to generate HiPS data from all-sky HEALPix images.
We give an example below.

Note that this functionality is very limited, and for most applications you will want to use the
Java ``hipsgen`` tool or the graphical user interface to ``hipsgen`` from the Aladin desktop application.

To use `~hips.healpix_to_hips` you have to pass in the all-sky HEALPix data as a Numpy array
(so it has to completely fit into memory). For grayscale images, the HEALPix data array is
one-dimensional, RGB images with array shape ``(npix, 3)`` can be converted to JPEG HiPS tiles,
and RGBA (where A is the transparency channel) images with array shape ``(npix, 4)`` can be
converted to PNG HiPS tiles.

Some data is distributed directly in HEALPix format, e.g. from all-sky surveys like Planck.
Some data from high-energy telescopes like Fermi-LAT consists of event lists can be used
to compute HEALPix images. And WCS-based images can also be reprojected to HEALPix images
using e.g. `reproject <https://reproject.readthedocs.io/en/stable/healpix.html>`__.
For these use cases `~hips.healpix_to_hips` can be used for the final all-sky HEALPix
map to HiPS conversion step, giving you full flexibility over the processing and pixel
color scales etc from Python in the pre-processing steps.

Limitations
-----------

Currently the following limitations exist:

- No mosaic functionality from WCS images
  (a lot of work to implement)
- Only one HiPS resolution is generated at the moment
  (not hard to write a script to make multiple resolutions)
- No ``Allsky.fits`` generated yet
  (shouldn't be hard to generate)

Dataset
=======

bla bla

Example
=======

Generate HiPS:

.. code-block:: bash

    $ python docs/hipsgen.py

Open HiPS in Aladin Lite:

.. code-block:: bash

    $ cd test123
    $ python -m http.server
    # Then open http://localhost:8000/ in your webbrowser

Or open HiPS in Aladin Desktop:

.. code-block:: bash

    $ TODO: how to load the folder in Aladin

Here's the ``hipsgen.py`` script:

.. literalinclude:: hipsgen.py

