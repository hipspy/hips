===================================
 Drawing algorithm for HiPS clients
===================================
 
 This is a summary of drawing algorithms that can be used by a HiPS client willing to create a cutout/display a given HiPS  for a given WCS.

1. Naive algorithm (drawing based on affine transformations)
============================================================


1. Compute HiPS order corresponding to the requested image size/resolution. The attributes of HiPS properties needed for this are **hips_order** (order at the tile level) and **hips_tile_width** (number of pixels for tile width and height). If hips_tile_width is missing, a default value of 512 is assumed.

2. Compute the list of tiles corresponding to the image FoV: in Python, we can use healpy *query_disc* with a center corresponding to the center of the image and a radius equal to the maximum separation on the sky between the image center and all pixels in the image.

3. For each tile, compute the world coordinates (ra, dec) of the tile corner vertices, using healpy *boundaries* function.

4. For each tile, project vertices in image coordinates according to the requested WCS.

5. Tiles whose vertices image coordinates are outside of the view, ie all above or all below or all on the right or all on the left can be filtered out.

6. We extend the tile by 1 pixel in all directions in order to hide "stitches" with other tiles drawing.

7. Fetch (HTTP calls or from cache) all remaining needed tiles.

8. Actual drawing:

  a. We ‘split’ the image tile diagonally into 2 triangles.
  b. Consider the first triangle
  c. Compute the affine transformation to map this triangle image vertices with computed image coordinates.
  d. Draw the tile according to the affine transformation, applying a mask in order to draw only the first triangle.
  e. Repeat step c and d for the second triangle.
  
If the HiPS one wants to use has a *hips_frame* property different from ‘equatorial’ (for instance ‘galactic’), additional coordinate frame conversions are required at steps #2 and #3.
   
1b. Fixing the problem of distorted tiles
=========================================

While the algorithm previously described works fine for HiPS tiles not distorted, it brings some astrometry offsets for distorted tiles. This distortion is strongly visible in the HEALPix scheme for tiles at the boundary between the equatorial zone and the polar cap.
   An example of such distortions is shown in the example below (uncheck *Activate deformations reduction algorithm* to view the astrometry offsets):
   http://cds.unistra.fr/~boch/AL/test-reduce-deformations2.html 
    
To overcome this problem, Aladin Desktop and Aladin Lite use the following recursive strategy: for tiles either too large (one edge is >300 pixels or diagonal is > 150 pixels when projected) or too distorted (ratio of smaller diagonal on larger diagonal is smaller than 0.7):

* We consider 4 children tiles, dynamically generated from the pixels of their father. Each children tile has a width and height equal to half of its father’s width/height.
* For each children tile, we compute the world coordinates of its vertices, project them and either draw it if not too distorted or repeat the process by splitting again into 4 children tiles.
     
The recursion is limited by a maximum number of recursive steps (for 512x512 tiles, you are limited to a maximum of 9 steps as 2^9=512) and/or a maximum order (maximum order set arbitrarily at 19 in Aladin Desktop).

2. Slower, more precise algorithm
=================================
      
Contrary the previous algorithm which used affine transformations, the idea here for the drawing step is to scan the result image pixels, and for each of them interpolate (Nearest neighbour or bilinear) the value, ie compute the indexes of nearest neighbour(s), retrieve the values of these pixels and merge them to determine the value of the target pixel. This is very similar to what `reproject <https://github.com/astrofrog/reproject>`_ is doing. 
       
One challenge is that one needs to know how to find the tile and pixel corresponding to a given HEALPix index.
The correspondance between a HEALPix index and a pixel in a HiPS tile is given by a hpx2xy array (see method createHpx2xy in class *cds.tools.pixtools.Util* from `Aladin Desktop source code <http://aladin.u-strasbg.fr/java/download/AladinSrc.jar>`_.)

3. WCS header for FITS tiles
============================

It seems that the astrometry of a HiPS tile can be accurately described using a WCS header like this one (example for HiPS in equatorial frame, Norder 3, Npix 448):

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


HPX projection is supported by WCSLib.
It is understood by DS9. Support in other tools (reproject, Montage, etc) is unclear and has to be tested.

