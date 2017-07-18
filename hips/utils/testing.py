"""Utilities for HiPS package testing.

Not of use for users / outside this package.
"""
import os
from pathlib import Path
import pytest
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from .wcs import WCSGeometry


def get_hips_extra_file(filename):
    """Get `~pathlib.Path` for a file in ``hips-extra``.

    To make this work, clone this repo:
    https://github.com/hipspy/hips-extra
    and set an environment variable ``HIPS_EXTRA`` pointing to it.
    """
    path = Path(os.environ['HIPS_EXTRA'])
    return path / filename


def has_hips_extra():
    """Is hips-extra available? (bool)"""
    if 'HIPS_EXTRA' in os.environ:
        path = Path(os.environ['HIPS_EXTRA']) / 'datasets/samples/DSS2Red/properties'
        if path.is_file():
            return True
    return False


def requires_hips_extra():
    """Decorator to mark tests requiring ``hips-extra`` data."""
    skip_it = not has_hips_extra()
    reason = 'No hips-extra data available.'
    return pytest.mark.skipif(skip_it, reason=reason)


def make_test_wcs_geometry():
    wcs = WCS(naxis=2)
    wcs.wcs.ctype[0] = 'GLON-AIT'
    wcs.wcs.ctype[1] = 'GLAT-AIT'
    wcs.wcs.crval[0] = 0
    wcs.wcs.crval[1] = 0
    wcs.wcs.crpix[0] = 1000
    wcs.wcs.crpix[1] = 500
    wcs.wcs.cdelt[0] = -0.01
    wcs.wcs.cdelt[1] = 0.01
    return WCSGeometry(wcs, width=2000, height=1000)

    # geometry = WCSGeometry.create(
    #     skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
    #     width=2000, height=1000, coordsys='galactic',
    #     projection='AIT', cdelt=0.01, crpix=(1000, 500),
    # )
