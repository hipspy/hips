# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
from PIL import Image
from astropy.io import fits
from astropy_healpix import healpy as hp
from numpy.testing import assert_allclose

from ..healpix import healpix_to_hips, healpix_to_hips_tile
from ..healpix import hips_to_healpix


@pytest.mark.parametrize('file_format', ['fits', 'png'])
def test_healpix_to_hips(tmpdir, file_format):
    nside, tile_width = 4, 2
    npix = hp.nside2npix(nside)
    hpx_data = np.arange(npix, dtype='uint8')
    healpix_to_hips(
        hpx_data=hpx_data,
        tile_width=tile_width,
        base_path=tmpdir,
        file_format=file_format
    )

    # The test data is filled with np.arange(), here we reproduce the sum of the
    # indices in the nested scheme manually for comparison
    desired = hpx_data.reshape((-1, tile_width, tile_width))

    for idx, val in enumerate(desired):
        filename = str(tmpdir / f'Norder1/Dir0/Npix{idx}.{file_format}')
        if file_format is 'fits':
            data = fits.getdata(filename)
            data = np.rot90(data, k=-1)
        else:
            data = np.array(Image.open(filename))
            data = data.T
        assert_allclose(val, data)

    properties = (tmpdir / 'properties').read_text(encoding=None)
    assert file_format in properties

def test_hips_to_healpix(tmpdir):
    nside, tile_width = 4, 2
    npix = hp.nside2npix(nside)
    healpix_data = np.arange(npix, dtype='uint8')

    n_tiles = healpix_data.size // tile_width ** 2

    tiles = []
    for tile_idx in range(n_tiles):
        tiles.append(healpix_to_hips_tile(hpx_data=healpix_data, tile_width=tile_width,
                                          tile_idx=tile_idx, file_format='fits'))

    healpix_map = hips_to_healpix(hips_url='http://alasky.u-strasbg.fr/Pan-STARRS/DR1/g',
                                  hips_tiles=tiles,
                                  healpix_pixels=healpix_data)
