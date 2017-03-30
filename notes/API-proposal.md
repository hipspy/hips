# HIPS Python package API proposal

## What is this?

* This is an API proposal for a Python HIPS client,
  i.e. small code examples demonstrating use cases we'd like to support.
* The plan is to implement this as a GSoC 2017 project.
* Feedback on this proposal (or even completely different ideas) highly welcome!
* Specifically: if you want to work with HIPS from Python, will this
  let you do what you want?
* For now we're focused on HIPS image fetching and drawing,
  but ideally the package would extend to HIPS catalog fetching in the future,
  and maybe even HIPS generation. So ideas / proposals on that are also welcome,
  but from our side aren't high priority for now.
 
## To be discussed

Here we list open questions to be discussed:

* Should we make a separate implementation proposal document?
  Or rename this document to HIPS proposal and put information on
  how the implementation should be done here?
* I found writing down the high-level API difficult, because it's not clear
  yet what parameters / mode of operation the low-level API has.
  Should we focus on the low-level API first?
* What objects to take as input / output?
  Header, WCS, ImageHDU, Filename?
  Low-level API should only work with WCS and shape (not coupled to FITS),
  but for the convenience high-level API it's not clear.
  Maybe look at `reproject` and mirror what they did?
* How to handle color images in the high-level API?
  Probably 3-dim Numpy arrays like e.g. scikit-image does, no?
  See http://scikit-image.org/docs/dev/user_guide/numpy_images.html#color-images
* How to do JPEG and PNG I/O? Is it clear that we should use Pillow
  or should we consider e.g. https://imageio.github.io/ ?
 

## High-level API

In this section we describe the high-level API for the most common use cases.
Users that want full control over what happens would use the low-level API.
Implementing the high-level API will be simple and not much code.

### Make a WCS image

FITS images consist of the pixel data, which in Python / Astropy is represented
by a Numpy array of shape `(ny, nx)`, and a header specifying a WCS that maps
sky to pixel coordinates. A common use case is that a user has such an image
and wants to make matching images from multi-wavelength HIPS data.

    from astropy.io import fits
    from hips import make_image_wcs
    
    header = fits.getheader('image.fits')
    data = make_image_wcs(header=header, survey='P/SDSS9/g')
    # data is a 2-dim numpy array (3-dim for color RGB images)
    

The `data` contains the pixel data from the given survey only,
the input `header` can be used for that image as well
(TODO: needs to be extended with third dimention for color image?
Should we introduce a simple SkyImage class to help with that, or
provide helper functions?)
The user could save that to a FITS file (or a JPEG or PNG file),
or do an analysis or plotting of the images.

A variation on this use case is that the user makes the header from scratch: 
http://astropy.readthedocs.io/en/latest/wcs/index.html#building-a-wcs-structure-programmatically

Note that `astropy.io.fits.Header` and `astropy.wcs.WCS` are mostly equivalent
for our purposes here, i.e. everywhere we take a `header`, we could also take a `WCS`.
See http://reproject.readthedocs.io/en/stable/celestial.html#interpolation .
The main difference is that sometimes the WCS object doesn't contain the information
on data array shape `(ny, nx)`.

The `make_image_wcs` function should expose a few more options to control
how the image gets made:
* `hpx_order` -- Healpix order of tiles to fetch (can be auto-computed from WCS so
  that it's a bit finer than the image pixels)
* `hips_timeout` -- Timeout for HIPS tile fetching
* Other HIPS parameters, like which server to use, ...


### Make a HEALPIX image

HIPS pixels are HEALPIX pixels on the sky. So it can be simplest to just
fetch the pixels you want and then continue processing them as HEALPIX data
locally. For this use case, we provide the `make_image_hpx` function:

    from hips import make_image_hpx
    data = make_image_hpx(survey=P/SDSS9/g', order=7)
    # data is a 1-dim numpy array (TODO: color?)

Now the user can save the HEALPIX data to file or work with it using `healpy` or `reproject`
The `order` parameter is the order of the output.
Under the hood tiles of size `(512, 512)` and `order-9` are fetched.

TBD: do we support some sparse HEALPIX format, or only fetching all-sky data?
What format for sparse HEALPIX? Two Numpy arrays (`ipix`, `val`)?

### Find and explore HIPS data

It could be nice to find and explore HIPS data from the Python interactive
terminal or a Jupyter notebook.

Maybe for http://aladin.u-strasbg.fr/hips/list there could be a function
that returns a listing of the available data.

And for each survey like http://alasky.unistra.fr/SDSS/DR9/band-g/ there
could be a function that lists the parameters for a given survey.

    from hips import get_hips_list, get_hips_info
    
    hips_list = get_hips_list(url='http://aladin.u-strasbg.fr/hips/list')
    # hips_list can be printed and queried, maybe some small class,
    # or an existing data structure like an `astropy.table.Table`

    hips_info = get_hips_info(survey=P/SDSS9/g')
    # hips_info is a dict or maybe we write a HIPSInfo class?

Later we should probably also add a widget for the Jupyter notebook that
gives a "preview" of a given survey using Aladin Lite, i.e. that makes it
easier to find surveys of interest.

It would also be nice to have utility functions to (partly) download HIPS data,
e.g. to copy over HIPS data from a server to a given local folder for later offline
use. Usually one would do this for a given sky region of interest, or only for
low-resolution maps, not the full HIPS data.

Everything in this section is low priority, as it can be done with the existing
web pages and clients (Aladin & Aladin Lite) already.

## Low-level API

The low-level API consists of functions and classes that let advanced users
do all the steps individually. E.g. the steps for the one function `make_image_wcs`
mentioned above could be:

1. Compute tiles needed to make the image
2. Check which tiles are available in a local cache
3. Fetch and cache the missing tiles.
   There might be re-try logic for requests that time out, or caching on disk if a RAM upper bound is reached.
4. Draw the tiles into the image
   Probably there will be a precise & slow drawing method, as well as an approximate & fast method
5. By default, probably delete tiles from the local cache, no?

One key question is how the tile cache(s) are implemented.
- in-memory or on-disk or both possible? who controls when the disk is used?
  We could either have a fixed-size in-memory cache and (optionally) a fixed-size disk cache.
  Or we could by default have no limit on the cache size and the user has to set a limit if they want to.
- implemented from scratch e.g. as a Python dict or using some DB solution such as SQLite or some document store?
- need to support adding tiles from async code?
- what is the index, i.e. key to store and look up tiles?
  Combine healpix pixel index with other parameters like survey name string, ...?
  Need a single index or have a multi-index with those parameters?
 
We'll have to discuss how to organise the code. Hopefully separating ths parts won't be too hard.

Here's a first quick guess at possible classes

* HipsTile -- represents one tile
* HipsTileMeta -- represents metadata for one tile
* HipsTileList -- a list of tiles

* HipsTileCache -- the central piece, where tiles are stored
* HipsTileFetcher -- fetch list of tiles and put it in the cache
* Where to put I/O code for FITS / PNG / JPEG?
  Do we cache pixel and metadata separately? Or just thow binary blobs for FITS / PNG / JPEG in the tile cache?

* HipsImageGeometry -- compute tile list and corners for given WCS
* HipsImageDrawer -- draw tiles onto a WCS image 

We can, but don't have to do a full HIPS package design before starting to implement it.
Probably starting with something simple that supports the implementation of the few high-level use cases
listed above in a modular way (that separates e.g. tile computation from tile download from tile drawing)
would be best. I.e. write down a clean implementation of the high-level functions listed above using
actual Python code using low-level classes.
Then implement the low-level classes to exactly support that functionality.

### TODO

TODO: summarise low-level API, to show how it works.

### HipsTileCache

TODO: summarise API

### HIPSImageDrawer

TODO: summarise API. Should this be a class or a function?
Maybe a class would be good, because it lets us split computation of steps into methods,
such as: first compute pixel corner positions, then the affine transformation parameters
for each tile, then apply the transformation to do the actual drawing.

