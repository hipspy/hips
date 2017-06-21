# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.tests.helper import remote_data
from ..tile import HipsTile

@remote_data
def test_fetch():
    fits_tile = HipsTile.fetch('fits', 'http://alasky.unistra.fr/2MASS/H/Norder6/Dir30000/Npix30889.fits')
    jpg_tile = HipsTile.fetch('jpg', 'http://alasky.unistra.fr/2MASS/H/Norder6/Dir30000/Npix30889.jpg')

    shape_fits_precomp = (512, 512)
    shape_jpg_precomp = (512, 512, 3)
    data_precomp = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
    assert fits_tile.data.shape == shape_fits_precomp
    assert jpg_tile.data.shape == shape_jpg_precomp
    assert list(fits_tile.data[510][:12]) == data_precomp

def test_read_write():
    fits_tile = HipsTile.read('fits', 'Npix30889.fits')
    jpg_tile = HipsTile.read('jpg', 'Npix30889.jpg')

    shape_fits_precomp = (512, 512)
    shape_jpg_precomp = (512, 512, 3)
    data_precomp = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
    assert (fits_tile.data.shape) == shape_fits_precomp
    assert (jpg_tile.data.shape) == shape_jpg_precomp
    assert list(fits_tile.data[510][:12]) == data_precomp

    fits_tile.write('test_file.fits')
    jpg_tile.write('test_file.jpg')

    path_fits = fits_tile.path / 'test_file.fits'
    path_jpg = jpg_tile.path / 'test_file.jpg'
    assert True == path_fits.is_file()
    assert True == path_jpg.is_file()
