"""Basic example how to plot a sky image with the hips package"""
from astropy.coordinates import SkyCoord
from hips import WCSGeometry, make_sky_image

# Compute the sky image
geometry = WCSGeometry.create(
    skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
    width=2000, height=1000, fov="3 deg",
    coordsys='galactic', projection='AIT',
)
hips_survey = 'CDS/P/DSS2/red'
result = make_sky_image(geometry=geometry, hips_survey=hips_survey, tile_format='fits')
result.plot()

# Draw the sky image
# import matplotlib.pyplot as plt
# from astropy.visualization.mpl_normalize import simple_norm
# ax = plt.subplot(projection=geometry.wcs)
# norm = simple_norm(result.image, 'sqrt', min_percent=1, max_percent=99)
# ax.imshow(result.image, origin='lower', norm=norm, cmap='gray')

# import matplotlib.pyplot as plt
# plt.show()
