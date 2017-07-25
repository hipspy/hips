# Licensed under a 3-clause BSD style license - see LICENSE.rst
from pathlib import Path
import pytest
from astropy.tests.helper import remote_data
from numpy.testing import assert_equal, assert_allclose
from ...utils.testing import get_hips_extra_file, requires_hips_extra
from ..tile import HipsTileMeta
from ..allsky import HipsTileAllskyArray

TEST_CASES = [
    dict(
        label='fits',
        meta=dict(order=3, ipix=-1, file_format='fits'),
        url='http://alasky.unistra.fr/IRAC4/Norder3/Allsky.fits',
        filename='datasets/samples/IRAC4/Norder3/Allsky.fits',

        repr="HipsTileAllskyArray(format='fits', order=3, width=1728, "
             "height=1856, n_tiles=768, tile_width=64)",
        dtype='float32',
        shape=(1856, 1728),
        # This is the pixel with the maximum value, to make it easy to find
        pix_idx=([1198], [742]),
        pix_val=2174.190673828125,

        tile_shape=(64, 64),
        # This is the same pixel as above, with the max value in the all-sky image
        tile_idx=281,
        tile_pix_idx=[[46], [38]],
        tile_pix_val=2174.190673828125,

    ),
    dict(
        label='jpg-grayscale',
        meta=dict(order=3, ipix=-1, file_format='jpg'),
        url='http://alasky.unistra.fr/IRAC4/Norder3/Allsky.jpg',
        filename='datasets/samples/IRAC4/Norder3/Allsky.jpg',

        repr="HipsTileAllskyArray(format='jpg', order=3, width=1728, "
             "height=1856, n_tiles=768, tile_width=64)",
        dtype='uint8',
        shape=(1856, 1728),
        # This is the same pixel as used above in the FITS test case
        # For JPEG it's saturated at value 255 and not the unique max
        pix_idx=([1198], [742]),
        pix_val=255,

        tile_shape=(64, 64),
        # This is the same pixel as above, with the max value in the all-sky image
        tile_idx=281,
        tile_pix_idx=[[46], [38]],
        tile_pix_val=244,
    ),
    dict(
        label='jpg-rgb',
        meta=dict(order=3, ipix=-1, file_format='jpg'),
        url='http://alasky.unistra.fr/Fermi/Color/Norder3/Allsky.jpg',
        filename='datasets/samples/FermiColor/Norder3/Allsky.jpg',

        repr="HipsTileAllskyArray(format='jpg', order=3, width=1728, "
             "height=1856, n_tiles=768, tile_width=64)",
        dtype='uint8',
        shape=(1856, 1728, 3),
        pix_idx=([510], [5]),
        pix_val=[[34, 23, 5]],

        tile_shape=(64, 64, 3),
        tile_idx=0,
        tile_pix_idx=([0], [0]),
        tile_pix_val=[[62, 44, 30]],
    ),
]


def parametrize(labels=None):
    if labels:
        test_cases = [_ for _ in TEST_CASES if _['label'] in labels]
    else:
        test_cases = TEST_CASES
    ids = lambda _: _['label']
    return pytest.mark.parametrize('pars', test_cases, ids=ids)


def _read_tile(pars):
    meta = HipsTileMeta(**pars['meta'])
    filename = get_hips_extra_file(pars['filename'])
    return HipsTileAllskyArray.read(meta, filename)


@requires_hips_extra()
@parametrize()
def test_read(pars):
    # Check that reading tiles in various formats works,
    # i.e. that pixel data in numpy array format
    # has correct shape, dtype and values
    allsky = _read_tile(pars)

    assert repr(allsky) == pars['repr']
    assert allsky.meta.order == pars['meta']['order']
    assert isinstance(allsky.raw_data, bytes)

    data = allsky.data
    assert data.shape == pars['shape']
    assert data.dtype.name == pars['dtype']
    assert_allclose(allsky.data[pars['pix_idx']], pars['pix_val'])


@requires_hips_extra()
# JPEG encoding is lossy, so here we only run the FITS and PNG test cases
@parametrize(labels='fits')
def test_from_numpy(pars):
    tile = _read_tile(pars)
    tile2 = HipsTileAllskyArray.from_numpy(tile.meta, tile.data)
    assert_equal(tile.data, tile2.data)


@remote_data
@requires_hips_extra()
@parametrize()
def test_fetch(pars):
    # Check that tile HTTP fetch gives the same result as tile read from disk
    meta = HipsTileMeta(**pars['meta'])
    tile_fetch = HipsTileAllskyArray.fetch(meta, url=pars['url'])

    filename = get_hips_extra_file(pars['filename'])
    tile_read = HipsTileAllskyArray.read(meta, filename)

    assert tile_fetch == tile_read


@requires_hips_extra()
@parametrize()
def test_write(tmpdir, pars):
    # Check that tile I/O works, i.e. round-trips on write / read
    tile = _read_tile(pars)

    filename = str(tmpdir / Path(pars['filename']).name)
    tile.write(filename)
    tile2 = HipsTileAllskyArray.read(tile.meta, filename)

    assert tile == tile2


@requires_hips_extra()
@parametrize()
def test_tile(pars):
    allsky = _read_tile(pars)

    tile = allsky.tile(pars['tile_idx'])

    assert tile.data.shape == pars['tile_shape']
    assert_allclose(tile.data[pars['tile_pix_idx']], pars['tile_pix_val'])


@requires_hips_extra()
@parametrize(labels='fits')
def test_from_tiles(pars):
    # Check that ``from_tiles`` works properly
    # For now, we check that ``tiles`` and ``from_tiles`` round-trip
    # TODO: it would probably be better to test them separately,
    # asserting on each of the two step. Round-trip can work, if
    # the same mistake is made in each conversion step.
    allsky = _read_tile(pars)
    tiles = allsky.tiles

    # This is for debugging ...
    allsky.write('/tmp/allsky.fits')
    allsky2 = HipsTileAllskyArray.from_tiles(tiles)
    allsky2.write('/tmp/allsky2.fits')

    # TODO: at the moment `HipsTileAllskyArray` always does a JPG encoding,
    # it can't hold the numpy array data unchanged.
    # This still doesn't work, because when going ``allsky.tiles`` another
    # JPG encoding happens.
    data2 = HipsTileAllskyArray.tiles_to_allsky_array(tiles)
    assert_allclose(allsky.data, data2)
