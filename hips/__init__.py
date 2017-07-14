# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
A Python astronomy package for HiPS : Hierarchical Progressive Surveys.

At the moment a client for HiPS images, but other contributions
(HiPS catalogs or HiPS image generation) welcome!

* Code : https://github.com/hipspy/hips
* Docs : https://hips.readthedocs.io
* License : BSD-3 (see licenses folder for license file)
"""

# Affiliated packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
from ._astropy_init import *
# ----------------------------------------------------------------------------

if not _ASTROPY_SETUP_:
    # For egg_info test builds to pass, put package imports here.
    from .draw import *
    from .tiles import *
    from .utils.wcs import WCSGeometry
