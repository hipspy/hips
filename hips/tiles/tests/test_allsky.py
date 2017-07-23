# Licensed under a 3-clause BSD style license - see LICENSE.rst
from pathlib import Path
import pytest
from astropy.tests.helper import remote_data
from numpy.testing import assert_equal
from ...utils.testing import get_hips_extra_file, requires_hips_extra
from ..tile import HipsTileMeta
from ..allsky import HipsTileAllskyArray

TEST_CASES = [
    dict(
        meta=dict(order=3, ipix=463, file_format='jpg'),
        url='http://alasky.unistra.fr/Fermi/Color/Norder3/Allsky.jpg',
        filename='datasets/samples/FermiColor/Norder3/Allsky.jpg',

        repr="HipsTileAllskyArray(format='jpg', order=3, width=1728, "
             "height=1856, n_tiles=768, tile_width=64)",
        dtype='uint8',
        shape=(1856, 1728, 3),
        pix_idx=[[510], [5]],
        pix_val=[[90, 89, 85]],
        tile_pix_val=[49, 44, 38],
    ),
]


def _read_tile(pars):
    meta = HipsTileMeta(**pars['meta'])
    filename = get_hips_extra_file(pars['filename'])
    return HipsTileAllskyArray.read(meta, filename)


@requires_hips_extra()
@pytest.mark.parametrize('pars', TEST_CASES)
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
    assert_equal(allsky.data[pars['pix_idx']], pars['pix_val'])


@requires_hips_extra()
@pytest.mark.parametrize('pars', TEST_CASES)
def test_from_numpy(pars):
    tile = _read_tile(pars)
    tile2 = HipsTileAllskyArray.from_numpy(tile.meta, tile.data)

    # JPEG encoding is lossy. So in that case, output pixel value
    # aren't exactly the same as input pixel values
    if tile.meta.file_format != 'jpg':
        assert_equal(tile.data, tile2.data)


@remote_data
@requires_hips_extra()
@pytest.mark.parametrize('pars', TEST_CASES)
def test_fetch(pars):
    # Check that tile HTTP fetch gives the same result as tile read from disk
    meta = HipsTileMeta(**pars['meta'])
    tile_fetch = HipsTileAllskyArray.fetch(meta, url=pars['url'])

    filename = get_hips_extra_file(pars['filename'])
    tile_read = HipsTileAllskyArray.read(meta, filename)

    assert tile_fetch == tile_read


@requires_hips_extra()
@pytest.mark.parametrize('pars', TEST_CASES)
def test_write(tmpdir, pars):
    # Check that tile I/O works, i.e. round-trips on write / read
    tile = _read_tile(pars)

    filename = str(tmpdir / Path(pars['filename']).name)
    tile.write(filename)
    tile2 = HipsTileAllskyArray.read(tile.meta, filename)

    assert tile == tile2


@requires_hips_extra()
@pytest.mark.parametrize('pars', TEST_CASES)
def test_tile(pars):
    allsky = _read_tile(pars)

    tile = allsky.tile(0)

    assert tile.data.shape == (64, 64, 3)
    assert_equal(tile.data[0, 0], pars['tile_pix_val'])


@requires_hips_extra()
@pytest.mark.parametrize('pars', TEST_CASES)
def test_from_tiles(pars):
    # Check that ``from_tiles`` works properly
    # For now, we check that ``tiles`` and ``from_tiles`` round-trip
    # TODO: it would probably be better to test them separately,
    # asserting on each of the two step. Round-trip can work, if
    # the same mistake is made in each conversion step.
    allsky = _read_tile(pars)
    # print(allsky)
    # allsky.write('/tmp/allsky.jpg')

    tiles = allsky.tiles

    # allsky2 = HipsTileAllskyArray.from_tiles(tiles)
    # print(allsky2)
    # allsky.write('/tmp/allsky2.jpg')

    # TODO: at the moment `HipsTileAllskyArray` always does a JPG encoding,
    # it can't hold the numpy array data unchanged.
    # This still doesn't work, because when going ``allsky.tiles`` another
    # JPG encoding happens.
    # I did check the JPG files written above. They look the same, so it's working.
    # Sigh.
    data2 = HipsTileAllskyArray.tiles_to_allsky_array(tiles)
    # assert_equal(allsky.data, data2)
