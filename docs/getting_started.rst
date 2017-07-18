.. include:: references.txt

.. doctest-skip-all

.. _gs:

***************
Getting started
***************

This is a quick getting started guide for the Python `hips` package.

Make a sky image
================

To make a sky image with the `hips` package, follow the following three steps:

1. Specify the sky image geometry you want by creating a `~hips.utils.WCSGeometry` object::

    from astropy.coordinates import SkyCoord
    from hips.utils import WCSGeometry

    geometry = WCSGeometry.create(
         skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
         width=2000, height=1000, fov="3 deg",
         coordsys='galactic', projection='AIT',
    )


2. Specify the HiPS survey you want by creating a `~hips.HipsSurveyProperties` object.

   A good address that lists available HiPS data is http://aladin.u-strasbg.fr/hips/list ::

    from hips.tiles import HipsSurveyProperties
    url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
    hips_survey = HipsSurveyProperties.fetch(url)


3. Call the `~hips.make_sky_image` function to fetch the HiPS data
   and draw it, returning the sky image pixel data as a Numpy array::

    from hips.draw import make_sky_image

    data = make_sky_image(geometry, hips_survey, 'fits')


That's it. Go ahead and try it out for your favourite sky region and survey.

Now you can then save the sky image to local disk e.g. FITS file format::

    from astropy.io import fits
    hdu = fits.PrimaryHDU(data=data, header=geometry.fits_header)
    hdu.writeto('my_image.fits')

or plot and analyse the sky image however you like.

If you execute the example above, you will get this sky image which was plotted using `astropy.visualization.wcsaxes`

.. plot:: plot_fits.py


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

We'll add ddvance examples and detailed documentation once things have stabilised a bit.

For now, if you know Python, you can look at the code and tests to see what's available:
https://github.com/hipspy/hips

What next?
==========

That's it, now you've seen the main features of the `hips` package.
Note that there is API documentation explaining all available functions, classes and parameters.

If you have any questions, or find something not working or a missing feature,
please get in touch by posting on our Github issue tracker.
