# Licensed under a 3-clause BSD style license - see LICENSE.rst
import time
import numpy as np
from typing import List, Tuple, Union, Dict, Any, Iterator
from astropy.wcs.utils import proj_plane_pixel_scales
from skimage.transform import ProjectiveTransform, warp
from ..tiles import HipsSurveyProperties, HipsTile, HipsTileMeta
from ..tiles.tile import compute_image_shape
from ..utils import WCSGeometry, healpix_pixels_in_sky_image, hips_order_for_pixel_resolution

__all__ = [
    'HipsPainter',
]

__doctest_skip__ = [
    'HipsPainter',
]


# TODO for Adeel: add option "precise".
# Should be default "true" eventually, for now, can use "false" if it's very slow.
class HipsPainter:
    """Paint a sky image from HiPS image tiles.

    Paint HiPS tiles onto a ky image using a simple projective
    transformation method. The algorithm implemented is described
    here: :ref:`drawing_algo`.

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        An object of WCSGeometry
    hips_survey : str or `~hips.HipsSurveyProperties`
        HiPS survey properties
    tile_format : {'fits', 'jpg', 'png'}
        Format of HiPS tile

    Examples
    --------
    >>> from astropy.coordinates import SkyCoord
    >>> from hips import WCSGeometry
    >>> from hips import HipsSurveyProperties
    >>> from hips import HipsPainter
    >>> geometry = WCSGeometry.create(
    ...     skydir=SkyCoord(0, 0, unit='deg', frame='icrs'),
    ...     width=2000, height=1000, fov='3 deg',
    ...     coordsys='icrs', projection='AIT',
    ... )
    >>> url = 'http://alasky.unistra.fr/DSS/DSS2Merged/properties'
    >>> hips_survey = HipsSurveyProperties.fetch(url)
    >>> painter = HipsPainter(geometry, hips_survey, 'fits')
    >>> painter.draw_hips_order
    7
    >>> painter.run()
    >>> painter.image.shape
    (1000, 2000)
    """

    def __init__(self, geometry: WCSGeometry, hips_survey: Union[str, HipsSurveyProperties], tile_format: str) -> None:
        self.geometry = geometry
        self.hips_survey = HipsSurveyProperties.make(hips_survey)
        self.tile_format = tile_format
        self._tiles = None
        self.float_image = None
        self._stats: Dict[str, Any] = {}

    @property
    def image(self) -> np.ndarray:
        """Computed sky image (`~numpy.ndarray`).

        * The ``dtype`` is always chosen to match the tile ``dtype``.
          This is ``uint8`` for JPG or PNG tiles,
          and can be e.g. ``int16`` or ``float32`` for FITS tiles.
        * The output shape is documented here: `~HipsPainter.shape`.
        """
        return self.float_image.astype(self.tiles[0].data.dtype)

    @property
    def draw_hips_order(self) -> int:
        """Compute HiPS tile order matching a given image pixel size."""
        # Sky image angular resolution (pixel size in degrees)
        resolution = np.min(proj_plane_pixel_scales(self.geometry.wcs))
        desired_order = hips_order_for_pixel_resolution(self.hips_survey.tile_width, resolution)
        # Return the desired order, or the highest resolution available.
        # Note that HiPS never has resolution less than 3,
        # and that limit is handled in _get_hips_order_for_resolution
        return np.min([desired_order, self.hips_survey.hips_order])

    @property
    def tile_indices(self):
        """Get list of index values for HiPS tiles."""
        return healpix_pixels_in_sky_image(
            geometry=self.geometry,
            order=self.draw_hips_order,
            healpix_frame=self.hips_survey.astropy_frame,
        )

    def projection(self, tile: HipsTile) -> ProjectiveTransform:
        """Estimate projective transformation on a HiPS tile."""
        corners = tile.meta.skycoord_corners.to_pixel(self.geometry.wcs)
        src = np.array(corners).T.reshape((4, 2))
        dst = tile_corner_pixel_coordinates(tile.meta.width)
        pt = ProjectiveTransform()
        pt.estimate(src, dst)
        return pt

    def _fetch_tiles(self) -> Iterator[HipsTile]:
        """Generator function to fetch HiPS tiles from a remote URL."""
        for healpix_pixel_index in self.tile_indices:
            tile_meta = HipsTileMeta(
                order=self.draw_hips_order,
                ipix=healpix_pixel_index,
                frame=self.hips_survey.astropy_frame,
                file_format=self.tile_format,
            )
            url = self.hips_survey.tile_url(tile_meta)
            tile = HipsTile.fetch(tile_meta, url)
            yield tile

    @property
    def tiles(self) -> List[HipsTile]:
        """List of `~hips.HipsTile` (cached on multiple access)."""
        # TODO: add progress bar reporting here???
        # Do it in a separate pull request
        # It has to work in the terminal and Jupyter notebook
        # Users have to be able to turn it off
        # So you have an option for it.
        # Maybe if you add it now, make it off by default.
        if self._tiles is None:
            self._tiles = list(self._fetch_tiles())

        return self._tiles

    def warp_image(self, tile: HipsTile) -> np.ndarray:
        """Warp a HiPS tile and a sky image."""
        return warp(
            tile.data,
            self.projection(tile),
            output_shape=self.geometry.shape,
            preserve_range=True,
        )

    def run(self) -> np.ndarray:
        """Draw HiPS tiles onto an empty image."""
        t0 = time.time()
        self.make_tile_list()
        t1 = time.time()
        self._stats['fetch_time'] = t1 - t0

        t0 = time.time()
        self.draw_all_tiles()
        t1 = time.time()
        self._stats['draw_time'] = t1 - t0

        # Todo for Adeel: copy over the stats dir to the DrawResult
        # and print it out nicely for the user in the report.
        # TODO: could add more code here that e.g. tries to measure memory usage
        # this could be done with https://pypi.python.org/pypi/psutil
        # or you could just compute the size of `raw_data` and `data` for each tile and sum them up
        # and also measure the memory used by the output sky image in MB
        # Other useful info: number of tiles fetched

    def make_tile_list(self):
        # Fetch all tiles needed
        parent_tiles = self.tiles

        # TODO for Adeel: implement distortion correction here.
        # Create new list of tiles, where some have been replaced by 4 children.
        # Suggestion: for now, just split once, no recursion.
        # Leave TODO, to discuss with Thomas next week.
        # See also: https://github.com/hipspy/hips/issues/92

        # For now, we just create a 1:1 copy
        tiles = []
        for tile in parent_tiles:
            tiles.append(tile)

        self.draw_tiles = tiles

    def _make_empty_sky_image(self):
        shape = compute_image_shape(
            width=self.geometry.shape.width,
            height=self.geometry.shape.height,
            fmt=self.tile_format,
        )
        return np.zeros(shape, dtype=np.float32)

    def draw_all_tiles(self):
        """Make an empty sky image and draw all the tiles."""
        image = self._make_empty_sky_image()

        # TODO: this is the second place where we should add
        # progress reporting
        for tile in self.draw_tiles:
            tile_image = self.warp_image(tile)
            # TODO: put better algorithm here instead of summing pixels
            # this can lead to pixels that are painted twice and become to bright
            image += tile_image

        # Store the result
        self.float_image = image

    def plot_mpl_hips_tile_grid(self) -> None:
        """Plot output image and HiPS grid with matplotlib.

        This is mainly useful for debugging the drawing algorithm,
        not something end-users will call or need to know about.
        """
        import matplotlib.pyplot as plt
        for tile in self.tiles:
            corners = tile.meta.skycoord_corners.transform_to(self.geometry.celestial_frame)
            ax = plt.subplot(projection=self.geometry.wcs)
            opts = dict(color='red', lw=1, )
            ax.plot(corners.data.lon.deg, corners.data.lat.deg,
                    transform=ax.get_transform('world'), **opts)
        ax.imshow(self.image, origin='lower')


def measure_tile_lengths(corners: Tuple[np.ndarray, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """Compute length of tile edges and diagonals.

    Parameters
    ----------
    corners : tuple of `~numpy.ndarray`
        Tile corner pixel coordinates ``(x, y)``

    Returns
    -------
    edges : `~numpy.ndarray`
        Tile edge pixel lengths.
        Entries: 0 -> 1, 1 -> 2, 2 -> 3, 3 -> 0
    diagonals : `~numpy.ndarray`
        Tile diagonal pixel lengths
        Entries: 0 -> 2, 1 -> 3
    """
    x, y = corners

    def dist(i: int, j: int) -> float:
        """Compute distance between two points."""
        return np.sqrt((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2)

    edges = [dist((i + 1) % 4, i) for i in range(4)]
    diagonals = [dist(0, 2), dist(1, 3)]

    return np.array(edges), np.array(diagonals)


def is_tile_distorted(corners: tuple) -> bool:
    """Is the tile with the given corners distorted?

    The criterion implemented here is described on the
    :ref:`drawing_algo` page, as part of the tile drawing algorithm.
    """
    edges, diagonals = measure_tile_lengths(corners)
    diagonal_ratio = min(diagonals) / max(diagonals)

    return bool(
        max(edges) > 300 or
        max(diagonals) > 150 or
        diagonal_ratio < 0.7
    )


def tile_corner_pixel_coordinates(width) -> np.ndarray:
    """Tile corner pixel coordinates for projective transform.

    Note that in this package we flip pixel data from JPEG and PNG
    to be consistent with FITS tile orientation on read.
    For that reason we can treat all tiles the same here and in other
    places in the package, and assume the FITS tile orientation is given.

    The order of corners below is chosen such that it matches the order
    of the pixel corner sky coordinates from ``healpix_pixel_corners``:

    - north
    - west
    - south
    - east

    and then gives correct results when used to compute the projective transform for tile drawing.
    """
    w = width - 1
    return np.array([
        [w, 0],  # north
        [w, w],  # west
        [0, w],  # south
        [0, 0],  # east
    ])


def plot_mpl_single_tile(geometry: WCSGeometry, tile: HipsTile, image: np.ndarray) -> None:
    """Draw markers on the output image (mainly used for debugging).

    The following denotes their correspondence:
    * red <=> North
    * green <=> West
    * blue <=> South
    * yellow <=> East

    Parameters
    ----------
    geometry : `~hips.utils.WCSGeometry`
        Geometry of the output image
    tile : HipsTile
        HiPS tile
    image : np.ndarray
        Image containing HiPS tiles
    """
    import matplotlib.pyplot as plt
    corners = tile.meta.skycoord_corners.transform_to(geometry.celestial_frame)
    colors = ['red', 'green', 'blue', 'yellow']
    ax = plt.subplot(projection=geometry.wcs)
    for index, corner in enumerate(corners):
        opts = dict(s=80, color=colors[index])
        ax.scatter(corner.data.lon.deg, corner.data.lat.deg,
                   transform=ax.get_transform('world'), **opts)
    ax.imshow(image, origin='lower')
