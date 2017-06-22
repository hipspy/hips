# Licensed under a 3-clause BSD style license - see LICENSE.rst

from astropy.coordinates import SkyCoord
from astropy.tests.helper import remote_data

from hips.tiles import HipsSurveyProperties
from hips.utils import WCSGeometry
from ..simple import make_sky_image


@remote_data
def test_make_sky_image():
    url = 'https://raw.githubusercontent.com/hipspy/hips/master/hips/tiles/tests/data/properties.txt'
    hips_survey = HipsSurveyProperties.fetch(url)

    shape = (1000, 2000)
    y_center, x_center = shape[0] / 2, shape[1] / 2
    skycoord = SkyCoord(0, 0, unit="deg")
    wcs_geometry = WCSGeometry.create(skydir=skycoord, shape=shape, coordsys='CEL', projection='AIT', cdelt=0.01,
                                      crpix=(y_center, x_center))
    make_sky_image(wcs_geometry, hips_survey)
