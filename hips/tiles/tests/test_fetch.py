# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
from astropy.tests.helper import remote_data
from numpy.testing import assert_allclose, assert_equal
from ..fetch import fetch_tiles
from ..survey import HipsSurveyProperties
from ..tile import HipsTileMeta

TILE_FETCH_TEST_CASES = [
    dict(
        tile_indices=[69623, 69627, 69628, 69629, 69630, 69631],
        is_missing=[False, False, False, False, False, False],
        tile_format='fits',
        order=7,
        url='http://alasky.unistra.fr/DSS/DSS2Merged/properties',
        progress_bar=True,
        data=[2101, 1945, 1828, 1871, 2079, 2336],
    ),
    dict(
        tile_indices=[69623,
                      9999999,  # missing
                      69628,
                      9999999,  # missing
                      9999999,  # missing
                      69631],
        is_missing=[False, True, False, True, True, False],
        tile_format='fits',
        order=7,
        url='http://alasky.unistra.fr/DSS/DSS2Merged/properties',
        progress_bar=True,
        data=[2101, 0, 1828, 0, 0, 2336],
    ),
]


def make_tile_metas(hips_survey, pars):
    for healpix_pixel_index in pars['tile_indices']:
        yield HipsTileMeta(
            order=pars['order'],
            ipix=healpix_pixel_index,
            frame=hips_survey.astropy_frame,
            file_format=pars['tile_format'],
        )


@pytest.mark.parametrize('pars', TILE_FETCH_TEST_CASES)
@remote_data
def test_fetch_tiles(pars):
    hips_survey = HipsSurveyProperties.fetch(pars['url'])

    tile_metas = list(make_tile_metas(hips_survey, pars))

    tiles = fetch_tiles(
        tile_metas, hips_survey,
        progress_bar=pars['progress_bar'],
    )

    for idx, val in enumerate(pars['data']):
        assert_allclose(tiles[idx].data[0][5], val)

    for idx, val in enumerate(pars['is_missing']):
        assert_equal(tiles[idx].is_missing, val)
