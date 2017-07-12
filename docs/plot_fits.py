"""This script plots the all-sky image following the example on getting started page"""
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from astropy.visualization.mpl_normalize import simple_norm

from hips import HipsSurveyProperties
from hips import make_sky_image
from hips.utils import WCSGeometry
import numpy as np
url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
hips_survey = HipsSurveyProperties.fetch(url)
geometry = WCSGeometry.create_simple(
    skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
    width=2000, height=1000, fov="3 deg",
    coordsys='galactic', projection='AIT'
)
data = make_sky_image(geometry=geometry, hips_survey=hips_survey, tile_format='fits')
ax = plt.subplot(projection=geometry.wcs)
norm = simple_norm(data, 'sqrt')
ax.imshow(data, origin='lower', norm=norm, cmap='gray')
