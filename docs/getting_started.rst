.. include:: references.txt

.. _gs:

***************
Getting started
***************

The example below shows a high level use case of the ``hips`` package.
It fetches a HiPS tile from a remote URL and draws it on a sky image.
Then it saves it on local disk in FITS file format.

>>> from astropy.io import fits
>>> from astropy.tests.helper import remote_data
>>> from hips.utils import WCSGeometry
>>> from hips.draw import make_sky_image
>>> from hips.tiles import HipsSurveyProperties
>>> geometry = WCSGeometry.create(
...     skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
...     shape=(1000, 2000), coordsys='GAL',
...     projection='AIT', cdelt=0.01, crpix=(1000, 500),
... )
>>> url = 'https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/DSS2Red/properties'
>>> hips_survey = HipsSurveyProperties.fetch(url)  # doctest: +REMOTE_DATA
>>> data = make_sky_image(geometry, hips_survey)
>>> hdu = fits.PrimaryHDU(data=data)
>>> hdu.writeto('my_image.fits')