.. include:: references.txt

.. doctest-skip-all

.. _gs:

***************
Getting started
***************

This is a quick getting started guide for the Python `hips` package.

Make a sky image
================

To draw a sky image from HiPS image tiles with the `hips` package, follow the following three steps:

1. Specify the sky image geometry you want by creating a `~hips.utils.WCSGeometry` object::

    from astropy.coordinates import SkyCoord
    from hips import WCSGeometry

    geometry = WCSGeometry.create(
         skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
         width=2000, height=1000, fov="3 deg",
         coordsys='galactic', projection='AIT',
    )

2. Specify the HiPS survey you want. You just need to provide a valid HiPS survey ID.

   A good address that lists available HiPS data is http://aladin.u-strasbg.fr/hips/list ::

    hips_survey = 'CDS/P/DSS2/red'

3. Call the `~hips.make_sky_image` function to fetch the HiPS data
   and draw it, returning an object of `~hips.HipsDrawResult`.
   By default a progress bar is shown for fetching and
   drawing HiPS tiles. For batch processing, this can be
   turned off by passing a keyword argument: `progress_bar=False`::

    from hips import make_sky_image
    result = make_sky_image(geometry, hips_survey, 'fits')

Of course, you could change the parameters to chose any sky image geometry and
available HiPS survey you like!

Work with the result
====================

The `~hips.HipsDrawResult` object from the last section makes it easy for you
to plot, save or analyse the sky image. To generate a quick-look plot of the sky image,
with rectangles outlining the HiPS tiles that were fetched and drawn to create the sky image::

    result.plot()

this will result in the following plot:

.. plot:: plot_fits.py

To save the sky image to a file::

    result.write_image('my_image.fits')

To analyse the data, or make a publication-quality plot, you can get the sky
image pixel data as a `numpy.ndarray`::

    >>> result.image

and the sky image `astropy.wcs.WCS` mapping pixel to sky coordinates via::

    >>> result.geometry.wcs

To print out summary information about the result::

    >>> print(result)

The `~hips.HipsDrawResult` object also gives access to the `~hips.HipsTile`
objects that were used for drawing the sky image, as well as other things.

Make a color sky image
======================

HiPS supports color images in ``jpg`` and ``png`` format.
Making a color sky image works the same as the grayscale image example above,
except that you get back a 3-dim Numpy array with ``(R, G, B)`` channels for ``jpg``
or ``(R, G, B, A)`` channels (``A`` is transparency) for ``png``.

Here's an example using ``jpg`` and http://alasky.u-strasbg.fr/Fermi/Color/ :

.. plot:: plot_jpg.py


HiPS data
=========

We plan to implement functionality to manage HiPS data, i.e. download it and cache it on a local disk.
This isn't available yet, at the moment we simply use Python lists of `~hips.HipsTile` objects,
which have a ``read`` method for a given filename and a ``fetch`` method for a given URL.

More advanced examples
======================

This package is under heavy development, it's changing quickly.

We'll add advanced examples and detailed documentation once things have stabilised a bit.

For now, if you know Python, you can look at the code and tests to see what's available:
https://github.com/hipspy/hips

What next?
==========

That's it, now you've seen the main features of the `hips` package.
Note that there is API documentation explaining all available functions, classes and parameters.

If you have any questions, or find something not working or a missing feature,
please get in touch by posting on our Github issue tracker.
