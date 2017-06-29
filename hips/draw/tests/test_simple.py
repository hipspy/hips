# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
import pytest
from astropy.tests.helper import remote_data
from numpy.testing import assert_allclose

from ..simple import make_sky_image, draw_sky_image
from ...tiles import HipsSurveyProperties, HipsTileMeta, HipsTile
from ...utils.testing import get_hips_extra_file, make_test_wcs_geometry, requires_hips_extra


def get_test_tiles():
    # TODO: check if this tile is inside our image
    tile1 = HipsTile.read(
        meta=HipsTileMeta(order=3, ipix=450, file_format='fits', tile_width=512),
        filename=get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix450.fits'),
    )

    tile2 = HipsTile.read(
        meta=HipsTileMeta(order=3, ipix=451, file_format='fits', tile_width=512),
        filename=get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix451.fits'),
    )

    return [tile1, tile2]


@requires_hips_extra()
def test_draw_sky_image():
    geometry = make_test_wcs_geometry(case=2)
    tiles = get_test_tiles()

    data = draw_sky_image(geometry, tiles)

    assert data.shape == geometry.shape
    assert data.dtype == np.float64
    assert np.sum(data) == 4575235421.5126467
    assert_allclose(data[400, 500:504], [2866.010141, 2563.691673, 2580.759013, 2746.608711])


@pytest.mark.xfail
@remote_data
def test_make_sky_image():
    url = 'https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/DSS2Red/properties'
    hips_survey = HipsSurveyProperties.fetch(url)
    geometry = make_test_wcs_geometry(case=2)

    data = make_sky_image(geometry, hips_survey)

    assert data.shape == geometry.shape
    assert data.dtype == np.float64
    assert_allclose(data[200, 994:1000], [3717.10091363, 3402.55292158, 3181.16613051, 2868.45175662, 2832.23001706,
                                          2779.23366271])
