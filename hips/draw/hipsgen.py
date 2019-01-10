# Licensed under a 3-clause BSD style license - see LICENSE.rst
import logging
import numpy as np
from ..tiles import HipsSurveyProperties, HipsTileAllskyArray, HipsTile, HipsTileMeta
from .healpix import healpix_to_hips_tiles
from pathlib import Path

__all__ = ["healpix_to_hips", "HipsSurvey"]

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
            '{name}', '{name}', '.', 'galactic', 1, {{imgFormat: '{imgFormat}'}}
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
    properties = HipsSurveyProperties(
        {
            "hips_tile_format": file_format,
            "hips_tile_width": tile_width,
            "hips_frame": frame,
        }
    )
    properties.write(path)

    # Make and write index.html
    txt = HTML_TEMPLATE.format_map({"name": "test123", "imgFormat": "fits"})
    path = base_path / "index.html"
    log.info(f"Writing {path}")
    path.write_text(txt)

    # Make and write tiles
    for tile in healpix_to_hips_tiles(hpx_data, tile_width, file_format, frame):
        path = base_path / tile.meta.tile_default_path
        log.info(f"Writing {path}")
        path.parent.mkdir(exist_ok=True, parents=True)
        tile.write(path)

    # Make and write allsky file
    hips_survey = HipsSurvey(base_path)
    allsky = hips_survey.make_allsky(order=0, file_format=file_format)
    path = base_path / f"Norder0/Allsky.{file_format}"
    log.info(f"Writing {path}")
    allsky.write(path)


# TODO: generalise and move to a better location
class HipsSurvey:
    """HiPS survey container.

    Represents one HiPS survey, acting as a manager
    to interact with the various pieces that make up a HiPS:

    - One `HipsSurveyProperties`
    - Many `HipsTile`
    - One `HipsTileAllskyArray` per order

    TODO: do we need several classes, for the different cases,
    or can they be handled by one `HipsSurvey` class?

    - in memory
    - on local disk
    - on server

    Functionality should include:

    - locate, read, write files
    - scan and print summary of contents (e.g. which orders / tiles are present)
    - copy / clone HiPS (possibly only small parts, with selections) locally and from servers
    - generate allsky from tiles? put this functionality here or somewhere else?

    Parameters
    ----------
    base_path : `pathlib.Path`
        Base path (folder where the ``properties`` file is located)
    """

    def __init__(self, base_path):
        self.base_path = base_path

    def make_allsky(self, order: int, file_format: str) -> HipsTileAllskyArray:
        tiles = self.read_tiles(order, file_format)
        # TODO: make from_tiles work with generators. For now we have to make a list
        tiles = list(tiles)
        return HipsTileAllskyArray.from_tiles(tiles)

    def read_tiles(self, order: int, file_format: str):
        properties = HipsSurveyProperties.read(self.base_path / 'properties')
        tile_path = self.base_path / f'Norder{order}'

        for path in tile_path.glob(f"Dir*/Npix*.{file_format}"):
            ipix = int(path.as_posix().split('/')[-1].split('.')[0][4:])
            frame = properties.hips_frame
            width = properties.tile_width
            meta = HipsTileMeta(order, ipix, file_format, frame, width)
            yield HipsTile.read(meta, path)
