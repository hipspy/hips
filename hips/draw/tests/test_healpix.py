# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import numpy as np
import healpy as hp
from PIL import Image
from astropy.io import fits
from numpy.testing import assert_allclose

from ..healpix import healpix_to_hips, hips_to_healpix


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
    hips_to_healpix(hips_url='http://alasky.u-strasbg.fr/Pan-STARRS/DR1/g',
                    npix=768,
                    hpx_output_path=tmpdir / 'panstarrs-g.hpx')

    healpix_map = hp.read_map(str(tmpdir / 'panstarrs-g.hpx'))
