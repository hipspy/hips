# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
import healpy as hp
from ..healpix import boundaries
from ..healpix import compute_image_pixels
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from numpy.testing import assert_allclose


def test_boundaries():
    order = 3
    nside = hp.order2nside(order)
    pix = 450
    theta, phi = boundaries(nside, pix)

    radec = SkyCoord(ra=phi, dec=np.pi/2 - theta, unit='radian', frame='icrs')

    """
    These HEALPix corner values were verified through Aladin Lite with the "Show
    healpix grid" option turned on. More information can be found on this GitHub
    issue: https://github.com/healpy/healpy/issues/393#issuecomment-305994042
    """
    radec_precomp = [[264.375,  258.75,  264.375,  270.],
                     [-24.624318,  -30.,  -35.685335,  -30.]]
    assert_allclose([radec.ra, radec.dec], radec_precomp)

def test_compute_image_pixels():
    order = 3
    nside = hp.order2nside(order)

    hdu = fits.open('https://github.com/gammapy/gammapy-extra/blob/master/datasets/catalogs/fermi/gll_psch_v08.fit.gz?raw=true')
    wcs = WCS(hdu[0].header)

    """
    These pixel values were obtained for the all-sky image located at:
    https://github.com/gammapy/gammapy-extra/blob/master/datasets/catalogs/fermi/gll_psch_v08.fit.gz?raw=true
    """
    pixels_precomp = \
    [  0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 20, 21, 22, 23,
      24, 25, 26, 27, 28, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 54, 55,
      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 77, 78, 79, 80, 81, 82, 83,
      84, 85, 86, 87, 88, 89, 90, 91, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113,
     114, 115, 116, 117, 118, 119, 120, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145,
     146, 147, 148, 149, 150, 151, 152, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178,
     179, 180, 181, 182, 183, 184, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210,
     211, 212, 213, 214, 215, 216, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243,
     244, 245, 246, 247, 248, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275,
     276, 277, 278, 279, 280, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308,
     309, 310, 311, 312, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340,
     341, 342, 343, 344, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373,
     374, 375, 376, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405,
     406, 407, 408, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438,
     439, 440, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470,
     471, 472, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503,
     504, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535,
     536, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568,
     583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600,
     616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 647,
     648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 676, 677,
     678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 701, 702, 703, 704, 705,
     706, 707, 708, 709, 710, 711, 712, 713, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731,
     732, 739, 740, 741, 742, 743, 744, 745, 746, 747, 752, 753, 754, 755, 756, 757, 758, 761,
     762, 763, 764, 765, 766, 767]

    pixels = compute_image_pixels(nside, hdu[0].data.shape, wcs)
    assert_allclose(pixels, pixels_precomp)
