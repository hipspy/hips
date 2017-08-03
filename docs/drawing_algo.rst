.. include:: references.txt

.. _drawing_algo:

=================
HiPS tile drawing
=================

This section describes the HiPS tile drawing algorithm implemented in this package,
to create a sky image for a given WCS.

The original description was for the algorithm implemented in Aladin Lite,
written by Thomas Boch. In the meantime, the algorithm implemented in this
Python package has deviated a bit, they are no longer the same.

The implementation is based on ``numpy``, ``astropy``, ``healpy`` and ``scikit-image``.

Naive algorithm
===============

This is a naive (one could also say: simple and fast) algorithm for drawing HiPS
tiles using affine transformations, implemented in the `~hips.HipsPainter`
class and usually executed by users via the high-level `~hips.make_sky_image` function.

First we compute and fetch the tiles that are needed for the given sky image:

#. The user specifies a `~hips.WCSGeometry`, which is a `astropy.wcs.WCS`
   as well as a width and height of the sky image to compute.
#. Compute HiPS order corresponding to the requested image size/resolution. The
   attributes of HiPS properties needed for this are ``hips_order`` (order at
   the tile level) and ``hips_tile_width`` (number of pixels for tile width and
   height). If hips_tile_width is missing, a default value of 512 is assumed.
#. Compute the list of tiles corresponding to the image FoV.
   This is done by computing the HiPS tile HEALPix pixel index for every pixel
   in the sky image and then computing the unique set.
#. Fetch (HTTP calls or from a local cache) all tiles in the list.

Then we draw the tiles one by one using these steps:

#. For each tile, compute the world coordinates of the tile corner
   vertices, using healpy ``boundaries`` function.
#. For each tile, project vertices in image coordinates according to the
   requested WCS (performing ICRS to Galactic frame transformation if
   the HiPS and sky image aren't in the same frame already).
#. We extend the tile by 1 pixel in all directions in order to hide "stitches"
   with other tiles drawing (TODO: not done yet. needed?)
#. The four corners uniquely define a projective transform between pixel coordinates
   on the tile and the output sky image. We use scikit-image to compute
   and apply that transform, which uses cubic spline interpolation under the hood.
   Thus the output is always float data, even if the input was integer RGB image data.

At the moment, we simply initialise the output sky image with pixel values of zero,
and then sum the sky images we get from each projected tile. This is inefficient,
and can result in incorrect pixel values at the lines corresponding to tile borders.
We plan to implement a better (more efficient and more correct) way to handle that soon.

Note that any algorithm using interpolation is not fully conserving flux or counts.
This might be a concern if you use the resulting sky images for data analysis.
It's your responsibility to decide if using this method is appropriate for your application or not!

Tile distortion issue
=====================

While the algorithm previously described works fine for HiPS tiles not
distorted, it brings some astrometry offsets for distorted tiles. This
distortion is strongly visible in the HEALPix scheme for tiles at the boundary
between the equatorial zone and the polar cap.

An example of such distortions is shown in the example below (uncheck *Activate
deformations reduction algorithm* to view the astrometry offsets):
http://cds.unistra.fr/~boch/AL/test-reduce-deformations2.html

To overcome this problem, Aladin Desktop and Aladin Lite use the following
recursive strategy: for tiles either too large (one edge is >300 pixels when projected) or too distorted (ratio of smaller
diagonal on larger diagonal is smaller than 0.7 and one of the diagonal is > 150 pixels when projected):

* We consider 4 children tiles, dynamically generated from the pixels of their
  father. Each children tile has a width and height equal to half of its
  father’s width/height.
* For each children tile, we compute the world coordinates of its vertices,
  project them and either draw it if not too distorted or repeat the process by
  splitting again into 4 children tiles.

The recursion is limited by a maximum number of recursive steps (for 512x512
tiles, you are limited to a maximum of 9 steps as 2^9=512) and/or a maximum
order (maximum order set arbitrarily at 19 in Aladin Desktop).

Precise algorithm
=================

.. note::

    The precise algorithm isn't implemented yet.

Contrary the previous algorithm which used affine transformations, the idea here
for the drawing step is to scan the result image pixels, and for each of them
interpolate (Nearest neighbour or bilinear) the value, ie compute the indexes of
nearest neighbour(s), retrieve the values of these pixels and merge them to
determine the value of the target pixel. This is very similar to what `reproject
<https://github.com/astrofrog/reproject>`_ is doing.

One challenge is that one needs to know how to find the tile and pixel
corresponding to a given HEALPix index. The correspondance between a HEALPix
index and a pixel in a HiPS tile is given by a ``hpx2xy`` array (see method
``createHpx2xy`` in class ``cds.tools.pixtools.Util`` from `Aladin Desktop
source code <http://aladin.u-strasbg.fr/java/download/AladinSrc.jar>`_.)

WCS for FITS tiles
==================

It seems that the astrometry of a HiPS tile can be accurately described using a
WCS header like this one (example for HiPS in equatorial frame, Norder 3, Npix
448):

.. code::

    NAXIS   =                    2 / number of data axes
    NAXIS1  =                  512 / length of data axis 1
    NAXIS2  =                  512 / length of data axis 1
    CRPIX1  =              -2047.5 / Coordinate reference pixel
    CRPIX2  =              -5631.5 / Coordinate reference pixel
    CD1_1   = -1.0986328125000E-02 / Transformation matrix (rot + scale)
    CD1_2   = -1.0986328125000E-02 / Transformation matrix (rot + scale)
    CD2_1   =  1.0986328125000E-02 / Transformation matrix (rot + scale)
    CD2_2   = -1.0986328125000E-02 / Transformation matrix (rot + scale)
    CTYPE1  = 'RA---HPX'            / Longitude in an HPX projection
    CTYPE2  = 'DEC--HPX'            /  Latitude in an HPX projection
    CRVAL1  =                   0. / [deg] Longitude at the reference point
    CRVAL2  =                   0. / [deg]  Latitude at the reference point
    PV2_1   =                   4 / HPX H parameter (longitude)
    PV2_2   =                   3 / HPX K parameter  (latitude)

HPX projection is supported by WCSLib. It is understood by DS9. Support in other
tools (reproject, Montage, etc) is unclear and has to be tested.

.. note::

    It seems that we can define a WCS for each tile.
    If so, this would allow us to simply use the ``reproject`` package
    to draw the tiles, which would be an alternative "precise" algorithm.
