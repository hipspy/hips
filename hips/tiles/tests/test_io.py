# Licensed under a 3-clause BSD style license - see LICENSE.rst
from pathlib import Path
from ..io import tile_default_url, tile_default_path


def test_tile_default_url():
    url = tile_default_url(order=9, ipix=54321, file_format='fits')
    assert url == 'Norder9/Dir50000/Npix54321.fits'


def test_tile_default_path():
    path = tile_default_path(order=9, ipix=54321, file_format='fits')
    assert path == Path('Norder9/Dir50000/Npix54321.fits')
