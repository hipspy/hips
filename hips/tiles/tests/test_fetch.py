# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.tests.helper import remote_data
from numpy.testing import assert_allclose
from ..fetch import HipsTileFetcher
from ..survey import HipsSurveyProperties
from ..tile import HipsTileMeta

class TestHipsTileFetcher:
    @classmethod
    def setup_class(cls):
        url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
        hips_survey = HipsSurveyProperties.fetch(url)

        tile_metas, tile_indices = [], [69623, 69627, 69628, 69629, 69630, 69631]
        for healpix_pixel_index in tile_indices:
            tile_meta = HipsTileMeta(
                order=7,
                ipix=healpix_pixel_index,
                frame=hips_survey.astropy_frame,
                file_format='fits',
            )
            tile_metas.append(tile_meta)

        cls.fetcher = HipsTileFetcher(tile_metas, hips_survey, progress_bar=False)

    @remote_data
    def test_tiles(self):
        tiles = self.fetcher.tiles
        assert_allclose(tiles[0].data[0][5:10], [2101, 1680, 1532, 1625, 2131])

    @remote_data
    def test_tiles_aiohttp(self):
        tiles = self.fetcher.tiles_aiohttp
        assert_allclose(tiles[0].data[0][5:10], [2101, 1680, 1532, 1625, 2131])
