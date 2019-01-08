# Licensed under a 3-clause BSD style license - see LICENSE.rst
import logging
import numpy as np
from ..tiles import HipsSurveyProperties
from .healpix import healpix_to_hips_tiles
from pathlib import Path

__all__ = ["healpix_to_hips"]

log = logging.getLogger(__name__)

HTML_TEMPLATE = r"""
<link rel="stylesheet" href="http://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css"/>
<script src="http://code.jquery.com/jquery-1.12.1.min.js"></script>
<script src="https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.js"></script>

<div id="aladin-lite-div" style="width:400px;height:400px;"></div>

<script type="text/javascript">

    var aladin = A.aladin('#aladin-lite-div',
        {{
            survey: '{name}',
            fov: 180,
            target: '0, 0',
            cooFrame: 'galactic'
        }});

    aladin.setImageSurvey(
        aladin.createImageSurvey(
            '{name}', '{name}', '', 'galactic', 1, {{imgFormat: '{imgFormat}'}}
        )
    );

</script>
"""


# TODO: change to class with each step as a method?
def healpix_to_hips(
        hpx_data: np.ndarray,
        tile_width: int,
        base_path: str,
        file_format: str,
        frame: str = "icrs",
):
    """Convert HEALPix image to HiPS.

    Directly writes files to output folder.

    Parameters
    ----------
    hpx_data : `~numpy.ndarray`
        Healpix data stored in the "nested" scheme.
    tile_width : int
        Width of the hips tiles.
    base_path : str or `~pathlib.Path`
        Base path.
    file_format : {'fits', 'jpg', 'png'}
        HiPS tile file format
    frame : {'icrs', 'galactic', 'ecliptic'}
        Sky coordinate frame
    """
    # Make and write properties file
    base_path = Path(base_path)
    base_path.mkdir(exist_ok=True, parents=True)
    path = base_path / "properties"
    log.info(f"Writing {path}")
    HipsSurveyProperties(
        {
            "hips_tile_format": file_format,
            "hips_tile_width": tile_width,
            "hips_frame": frame,
        }
    ).write(path)

    # Make and write index.html
    txt = HTML_TEMPLATE.format_map({
        "name": "test123",
        "imgFormat": "fits",
    })
    path = base_path / "index.html"
    log.info(f"Writing {path}")
    path.write_text(txt)

    # TODO: make and write Allsky.{file_format}

    # Make and write tiles
    for tile in healpix_to_hips_tiles(hpx_data, tile_width, file_format, frame):
        path = base_path / tile.meta.tile_default_path
        log.info(f"Writing {path}")
        path.parent.mkdir(exist_ok=True, parents=True)
        tile.write(path)
