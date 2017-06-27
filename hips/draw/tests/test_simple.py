# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
import pytest
from astropy.tests.helper import remote_data

from ..simple import make_sky_image, draw_sky_image
from ...tiles import HipsSurveyProperties, HipsTileMeta, HipsTile
from ...utils.testing import get_hips_extra_file, make_test_wcs_geometry, requires_hips_extra


def get_test_tiles():
    # TODO: check if this tile is inside our image
    tile1 = HipsTile.read(
        meta=HipsTileMeta(order=3, ipix=658, file_format='fits', tile_width=512),
        filename=get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix658.fits'),
    )

    tile2 = HipsTile.read(
        meta=HipsTileMeta(order=3, ipix=659, file_format='fits', tile_width=512),
        filename=get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix659.fits'),
    )

    return [tile1, tile2]


@pytest.mark.xfail
@requires_hips_extra()
def test_draw_sky_image():
    geometry = make_test_wcs_geometry(case=2)
    tiles = get_test_tiles()

    data = draw_sky_image(geometry, tiles)

    assert data.shape == geometry.shape
    assert data.dtype == np.float64

    assert data[0, 0] == 0.0


@remote_data
def test_make_sky_image():
    url = 'https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/DSS2Red/properties'
    hips_survey = HipsSurveyProperties.fetch(url)
    geometry = make_test_wcs_geometry(case=2)

    data = make_sky_image(geometry, hips_survey)

    assert data.shape == geometry.shape
    assert data.dtype == np.float64
    assert data[800, 1000] == 1794.7673494847763
