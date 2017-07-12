.. include:: references.txt

.. doctest-skip-all

.. _gs:

***************
Getting started
***************

This is a quick getting started guide for the Python `hips` package.

Make a sky image
----------------

To make a sky image with the `hips` package, follow the following three steps:

1. Specify the sky image geometry you want by creating a `~hips.utils.WCSGeometry` object::

    from astropy.coordinates import SkyCoord
    from hips.utils import WCSGeometry

    geometry = WCSGeometry.create_simple(
         skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
         width=2000, height=1000, fov="3 deg",
         coordsys='galactic', projection='AIT'
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

TODO: show how to plot the image with `astropy.visualization.wcsaxes`.

HiPS data
---------

TODO: write me

* Explain about tiles
* File formats
* Where the HiPS package stores data (in memory and on disk)


More advanced examples
----------------------

TODO: write me

* Show examples for the more low-level, but more configurable classes.

What next?
----------

That's it, now you've seen the main features of the `hips` package.
Note that there is API documentation explaining all available functions, classes and parameters.

If you have any questions, or find something not working or a missing feature,
please get in touch by posting on our Github issue tracker.
