"""Basic example how to plot a sky image with the hips package"""
from astropy.coordinates import SkyCoord
from hips import WCSGeometry, HipsPainter

# Compute the sky image
geometry = WCSGeometry.create(
    skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
    width=2000, height=1000, fov="3 deg",
    coordsys='galactic', projection='AIT',
)
hips_survey = 'IPAC/P/GLIMPSE360'

fetch_opts = dict(fetch_package='urllib', timeout=30, n_parallel=10)
painter = HipsPainter(geometry, hips_survey, 'jpg', fetch_opts=fetch_opts)
painter.run()
painter.plot_mpl_hips_tile_number_grid()
