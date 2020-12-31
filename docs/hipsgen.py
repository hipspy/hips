"""Example how to generate HiPS from HEALPix.

We will use
"""
import logging
import numpy as np
import hips
from astropy.coordinates import SkyCoord
from astropy_healpix import HEALPix


def make_healpix_data(hips_order, tile_width, file_format):
    """Silly example of HEALPix data.

    Angular distance in deg to (0, 0) as pixel values.
    """
    nside = tile_width * (2 ** hips_order)
    healpix = HEALPix(nside=nside)
    ipix = np.arange(healpix.npix)
    lon, lat = healpix.healpix_to_lonlat(ipix)
    coord = SkyCoord(lon, lat)
    center = SkyCoord(0, 0, unit="deg")
    data = coord.separation(center).deg

    if file_format == "fits":
        return data
    elif file_format == "jpg":
        data = data.astype("uint8")
        return np.moveaxis([data, data + 1, data + 2], 0, -1)
    elif file_format == "png":
        data = data.astype("uint8")
        return np.moveaxis([data, data + 1, data + 2, data + 3], 0, -1)
    else:
        raise ValueError()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    file_format = "png"
    hips_order = 3
    tile_width = 4

    hpx_data = make_healpix_data(hips_order, tile_width, file_format)

    hips.healpix_to_hips(
        hpx_data=hpx_data,
        hips_order=hips_order,
        tile_width=tile_width,
        base_path="test123",
        file_format=file_format,
    )
