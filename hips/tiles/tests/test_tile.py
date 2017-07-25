# Licensed under a 3-clause BSD style license - see LICENSE.rst
from pathlib import Path
import pytest
from astropy.tests.helper import remote_data
from numpy.testing import assert_allclose, assert_equal
from ...utils.testing import get_hips_extra_file, requires_hips_extra
from ..tile import HipsTileMeta, HipsTile


class TestHipsTileMeta:
    @classmethod
    def setup_class(cls):
        # Note: we're intentionally using positional args
        # to make sure tests fail if the order of args is changed
        cls.meta = HipsTileMeta(3, 450, 'fits', 'icrs', 512)

    def test_order(self):
        assert self.meta.order == 3

    def test_ipix(self):
        assert self.meta.ipix == 450

    def test_file_format(self):
        assert self.meta.file_format == 'fits'

    def test_frame(self):
        assert self.meta.frame == 'icrs'

    def test_width(self):
        assert self.meta.width == 512

    def test_repr(self):
        expected = "HipsTileMeta(order=3, ipix=450, file_format='fits', frame='icrs', width=512)"
        assert repr(self.meta) == expected

    def test_eq(self):
        assert self.meta == HipsTileMeta(3, 450, 'fits', 'icrs', 512)
        assert self.meta != HipsTileMeta(4, 450, 'fits', 'icrs', 512)

    def test_copy(self):
        meta = self.meta.copy()
        meta.ipix = 42
        assert self.meta.ipix == 450
        assert meta.ipix == 42

    def test_skycoord_corners(self):
        coord = self.meta.skycoord_corners
        assert_allclose(coord.data.lat.deg, [-24.624318, -30., -35.685335, -30.])
        assert_allclose(coord.data.lon.deg, [264.375, 258.75, 264.375, 270.])
        assert self.meta.skycoord_corners.frame.name == 'icrs'

    @staticmethod
    def test_skycoord_corners_galactic():
        meta = HipsTileMeta(order=3, ipix=450, file_format='fits', frame='galactic')
        coord = meta.skycoord_corners
        assert_allclose(coord.data.lat.deg, [-24.624318, -30., -35.685335, -30.])
        assert_allclose(coord.data.lon.deg, [264.375, 258.75, 264.375, 270.])
        assert coord.frame.name == 'galactic'

    def test_tile_url(self):
        url = self.meta.tile_default_url
        assert url == 'Norder3/Dir0/Npix450.fits'

    def test_tile_path(self):
        path = self.meta.tile_default_path
        assert path == Path('Norder3/Dir0/Npix450.fits')


HIPS_TILE_TEST_CASES = [
    dict(
        label='fits',
        meta=dict(order=3, ipix=463, file_format='fits'),
        url='http://alasky.unistra.fr/DSS/DSS2Merged/Norder3/Dir0/Npix463.fits',
        filename='datasets/samples/DSS2Red/Norder3/Dir0/Npix463.fits',

        dtype='int16',
        shape=(512, 512),
        pix_idx=[[510], [5]],
        pix_val=[3047],

        child_order=4,
        child_shape=(256, 256),
        child_ipix=[1852, 1853, 1854, 1855],
        child_pix_idx=[[255], [255]],
        child_pix_val=[2153, 2418, 2437, 2124],
    ),
    dict(
        label='jpg',
        meta=dict(order=3, ipix=463, file_format='jpg'),
        url='http://alasky.unistra.fr/Fermi/Color/Norder3/Dir0/Npix451.jpg',
        filename='datasets/samples/FermiColor/Norder3/Dir0/Npix451.jpg',

        dtype='uint8',
        shape=(512, 512, 3),
        pix_idx=[[510], [5]],
        pix_val=[[132, 116, 83]],

        child_order=4,
        child_shape=(256, 256, 3),
        child_ipix=[1852, 1853, 1854, 1855],
        child_pix_idx=[[255], [255]],
        child_pix_val=[[[245, 214, 211]], [[137, 97, 87]], [[255, 241, 225]], [[109, 95, 86]]],
    ),
    dict(
        label='png',
        meta=dict(order=6, ipix=6112, file_format='png'),
        url='http://alasky.unistra.fr/2MASS6X/2MASS6X_H/Norder6/Dir0/Npix6112.png',
        filename='datasets/samples/2MASS6XH/Norder6/Dir0/Npix6112.png',

        dtype='uint8',
        shape=(512, 512, 4),
        pix_idx=[[253], [5]],
        pix_val=[[15, 15, 15, 255]],

        child_order=7,
        child_shape=(256, 256, 4),
        child_ipix=[24448, 24449, 24450, 24451],
        child_pix_idx=[[255], [255]],
        child_pix_val=[[[17, 17, 17, 255]], [[13, 13, 13, 255]], [[15, 15, 15, 255]], [[20, 20, 20, 255]]],
    ),
]


def parametrize():
    ids = lambda _: _['label']
    return pytest.mark.parametrize('pars', HIPS_TILE_TEST_CASES, ids=ids)


class TestHipsTile:
    @staticmethod
    def _read_tile(pars):
        meta = HipsTileMeta(**pars['meta'])
        filename = get_hips_extra_file(pars['filename'])
        return HipsTile.read(meta, filename)

    @requires_hips_extra()
    @parametrize()
    def test_from_numpy(self, pars):
        tile = self._read_tile(pars)
        tile2 = HipsTile.from_numpy(tile.meta, tile.data)

        # JPEG encoding is lossy. So in that case, output pixel value
        # aren't exactly the same as input pixel values
        if tile.meta.file_format != 'jpg':
            assert_equal(tile.data, tile2.data)

    @requires_hips_extra()
    @parametrize()
    def test_read(self, pars):
        # Check that reading tiles in various formats works,
        # i.e. that pixel data in numpy array format
        # has correct shape, dtype and values
        tile = self._read_tile(pars)

        assert tile.meta.order == pars['meta']['order']
        assert isinstance(tile.raw_data, bytes)

        data = tile.data
        assert data.shape == pars['shape']
        assert data.dtype.name == pars['dtype']
        assert_equal(data[pars['pix_idx']], pars['pix_val'])

    @remote_data
    @requires_hips_extra()
    @parametrize()
    def test_fetch(self, pars):
        # Check that tile HTTP fetch gives the same result as tile read from disk
        meta = HipsTileMeta(**pars['meta'])
        tile_fetch = HipsTile.fetch(meta, url=pars['url'])

        filename = get_hips_extra_file(pars['filename'])
        tile_read = HipsTile.read(meta, filename)

        assert tile_fetch == tile_read

    @requires_hips_extra()
    @parametrize()
    def test_write(self, tmpdir, pars):
        # Check that tile I/O works, i.e. round-trips on write / read
        tile = self._read_tile(pars)

        filename = str(tmpdir / Path(pars['filename']).name)
        tile.write(filename)
        tile2 = HipsTile.read(tile.meta, filename)

        assert tile == tile2

    @requires_hips_extra()
    @parametrize()
    def test_children(self, pars):
        tile = self._read_tile(pars)
        child_data = [_.data[pars['child_pix_idx']] for _ in tile.children]
        child_ipix = [_.meta.ipix for _ in tile.children]

        assert tile.children[0].meta.order == pars['child_order']
        assert tile.children[0].data.shape == pars['child_shape']
        assert_equal(child_ipix, pars['child_ipix'])
        assert_equal(child_data, pars['child_pix_val'])
