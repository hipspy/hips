# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from astropy.tests.helper import remote_data
from numpy.testing import assert_allclose
from numpy.testing import assert_equal
from ..tile import HipsTile, HipsTileMeta
from ...utils.testing import get_hips_extra_file, requires_hips_extra

class TestHipsTile:

    fetch_read_pars = [
        dict(url='http://alasky.unistra.fr/DSS/DSS2Merged/Norder3/Dir0/Npix463.fits',
             full_path='datasets/samples/DSS2Red/Norder3/Dir0/Npix463.fits',
             file_name='Npix463.fits', file_format='fits', order=3, ipix=463),
        dict(url='http://alasky.unistra.fr/DSS/DSS2Merged/Norder3/Dir0/Npix463.jpg',
             full_path='datasets/samples/DSS2Red/Norder3/Dir0/Npix463.jpg',
             file_name='Npix463.jpg', file_format='jpg', order=3, ipix=463),
        dict(url='http://alasky.unistra.fr/2MASS6X/2MASS6X_H/Norder6/Dir0/Npix6112.png',
             full_path='datasets/samples/2MASS6XH/Norder6/Dir0/Npix6112.png',
             file_name='Npix6112.png', file_format='png', order=6, ipix=6112)
    ]

    @remote_data
    @requires_hips_extra()
    @pytest.mark.parametrize('pars', fetch_read_pars)
    def test_fetch_read(self, pars):
        meta = HipsTileMeta(order=pars['order'], ipix=pars['ipix'], file_format=pars['file_format'])
        tile_fetched = HipsTile.fetch(meta, url=pars['url'])

        full_path = get_hips_extra_file(pars['full_path'])
        tile_local = HipsTile.read(meta, full_path=full_path)

        assert tile_fetched == tile_local

    read_write_pars = [
        dict(full_path='datasets/samples/DSS2Red/Norder3/Dir0/Npix463.fits', file_name='Npix463.fits',
             file_format='fits', order=3, ipix=463, shape=(512, 512), tile_data=[3047], index=[[510], [5]]),
        dict(full_path='datasets/samples/DSS2Red/Norder3/Dir0/Npix463.jpg', file_name='Npix463.jpg',
             file_format='jpg', order=3, ipix=463, shape=(512, 512, 3), tile_data=[[10, 10, 10]], index=[[510], [5]]),
        dict(full_path='datasets/samples/2MASS6XH/Norder6/Dir0/Npix6112.png', file_name='Npix6112.png',
             file_format='png', order=6, ipix=6112, shape=(512, 512, 4), tile_data=[[19, 19, 19, 255]], index=[[253], [5]])
    ]

    @requires_hips_extra()
    @pytest.mark.parametrize('pars', read_write_pars)
    def test_read_write(self, tmpdir, pars):
        meta = HipsTileMeta(order=pars['order'], ipix=pars['ipix'], file_format=pars['file_format'])
        full_path = get_hips_extra_file(pars['full_path'])
        tile = HipsTile.read(meta, full_path)

        assert tile.data.shape == pars['shape']
        assert_equal(tile.data[pars['index']], pars['tile_data'])

        filename = str(tmpdir / pars['file_name'])
        tile.write(filename)
        tile2 = HipsTile.read(meta, full_path=filename)

        # TODO: Fix JPG write issue
        # assert tile == tile2

    def test_value_error(self):
        with pytest.raises(ValueError):
            meta = HipsTileMeta(order=3, ipix=463, file_format='jpeg')
            full_path = get_hips_extra_file('datasets/samples/DSS2Red/Norder3/Dir0/Npix463.jpg')
            HipsTile.read(meta, full_path)


class TestHipsTileMeta:
    @classmethod
    def setup_class(cls):
        cls.meta = HipsTileMeta(order=3, ipix=450, file_format='fits', frame='icrs', tile_width=512)

    def test_path(self):
        assert str(self.meta.path) == 'hips/tiles/tests/data'

    def test_filename(self):
        assert self.meta.filename == 'Npix450.fits'

    def test_full_path(self):
        assert str(self.meta.full_path) == 'hips/tiles/tests/data/Npix450.fits'

    def test_nside(self):
        assert self.meta.nside == 8

    def test_dst(self):
        dst = np.array([[511, 0], [511, 511], [0, 511], [0, 0]])
        assert_allclose(self.meta.dst, dst)

    def test_skycoord_corners(self):
        assert_allclose(self.meta.skycoord_corners.data.lat.deg, [-24.624318, -30., -35.685335, -30.])
        assert_allclose(self.meta.skycoord_corners.data.lon.deg, [264.375, 258.75, 264.375, 270.])
        assert self.meta.skycoord_corners.frame.name == 'icrs'

        meta = HipsTileMeta(order=3, ipix=450, file_format='fits', frame='galactic', tile_width=512)
        assert_allclose(meta.skycoord_corners.data.lat.deg, [-24.624318, -30., -35.685335, -30.])
        assert_allclose(meta.skycoord_corners.data.lon.deg, [264.375, 258.75, 264.375, 270.])
        assert meta.skycoord_corners.frame.name == 'galactic'
