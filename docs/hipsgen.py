"""Example how to generate HiPS from HEALPix.

We will use
"""
import logging
import numpy as np
import hips
from astropy.coordinates import SkyCoord
from astropy_healpix import HEALPix


def make_healpix_data():
    """Silly example of HEALPix data.
    Angular distance to
    """
    healpix = HEALPix(nside=4)
    ipix = np.arange(healpix.npix)
    lon, lat = healpix.healpix_to_lonlat(ipix)
    coord = SkyCoord(lon, lat)
    center = SkyCoord(0, 0, unit='deg')
    return coord.separation(center).deg


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    data = make_healpix_data()
    hips.healpix_to_hips(data, tile_width=4, base_path='test123', file_format='fits')
