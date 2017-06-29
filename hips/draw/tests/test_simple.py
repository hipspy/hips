# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from astropy.utils.data import get_pkg_data_filename
from numpy.testing import assert_allclose

from ..simple import make_sky_image, draw_sky_image, SimpleTilePainter
from ...tiles import HipsSurveyProperties, HipsTileMeta, HipsTile
from ...utils.testing import get_hips_extra_file, make_test_wcs_geometry, requires_hips_extra


def get_test_tiles():
    frames = dict({'equatorial': 'icrs', 'galactic': 'galactic', 'ecliptic': 'ecliptic'})
    filename = get_pkg_data_filename('../../tiles/tests/data/properties.txt')
    hips_survey = HipsSurveyProperties.read(filename)

    tile1 = HipsTile.read(
        meta=HipsTileMeta(order=3, ipix=450, file_format='fits', frame=frames[hips_survey.hips_frame], tile_width=512),
        filename=get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix450.fits'),
    )

    tile2 = HipsTile.read(
        meta=HipsTileMeta(order=3, ipix=451, file_format='fits', frame=frames[hips_survey.hips_frame], tile_width=512),
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
    assert data[400, 500] == 2866.0101409848185
    assert data[400, 501] == 2563.6916727348043


@pytest.mark.xfail
def test_make_sky_image():
    url = 'https://raw.githubusercontent.com/hipspy/hips-extra/master/datasets/samples/DSS2Red/properties'
    hips_survey = HipsSurveyProperties.fetch(url)
    geometry = make_test_wcs_geometry(case=2)
    data = make_sky_image(geometry, hips_survey)
    assert data.shape == geometry.shape
    assert data.dtype == np.float64
    assert data[200, 994] == 3717.10091363
    assert data[200, 995] == 3402.55292158


class TestSimpleTilePainter:
    @classmethod
    def setup_class(cls):
        geometry = make_test_wcs_geometry(case=2)
        tile = HipsTile.read(
            meta=HipsTileMeta(order=3, ipix=450, file_format='fits', frame='icrs', tile_width=512),
            filename=get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix450.fits'),
        )
        cls.simple_tile_painter = SimpleTilePainter(geometry, tile)

    def test_compute_corners(self):
        self.simple_tile_painter.compute_corners()
        assert_allclose(self.simple_tile_painter.corners[0], [728.54880122, 1453.32078085, 1662.33429379, 931.69072155])
        assert_allclose(self.simple_tile_painter.corners[1], [880.33972146, 997.1604671, 288.00518917, 175.4190427])
