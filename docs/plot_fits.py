"""Basic example how to plot a sky image with the hips package"""
from astropy.coordinates import SkyCoord
from hips import HipsSurveyProperties
from hips import make_sky_image
from hips.utils import WCSGeometry

# Compute the sky image
url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
hips_survey = HipsSurveyProperties.fetch(url)
geometry = WCSGeometry.create(
    skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
    width=2000, height=1000, fov="3 deg",
    coordsys='galactic', projection='AIT',
)
image = make_sky_image(geometry=geometry, hips_survey=hips_survey, tile_format='fits')

# Draw the sky image
import matplotlib.pyplot as plt
from astropy.visualization.mpl_normalize import simple_norm
ax = plt.subplot(projection=geometry.wcs)
norm = simple_norm(image, 'sqrt', min_percent=1, max_percent=99)
ax.imshow(image, origin='lower', norm=norm, cmap='gray')
