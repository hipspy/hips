---
title: 'A Python astronomy package for HiPS: Hierarchical Progressive Surveys'
tags:
- python
- astronomy
- science
- image-viewer
- image-processing

authors:
- name: Adeel Ahmad
  orcid: 0000-0001-5035-4497
  affiliation: 1

- name: Christoph Deil
  orcid: 0000-0002-4198-4005
  affiliation: 2

- name: Thomas Boch
  orcid: 0000-0001-5818-2781
  affiliation: 3

- name: Brigitta M Sipőcz
  orcid: 0000-0002-3713-6337
  affiliation: 4

- name: Axel Donath
  orcid:
  affiliation: 2

affiliations:
- name: National University of Computer and Emerging Sciences, Islamabad, Pakistan
  index: 1
- name: Max Planck Institute for Nuclear Physics, Heidelberg, Germany
  index: 2
- name: Université de Strasbourg, CNRS, Observatoire astronomique de Strasbourg
  index: 3
- name: Institute of Astronomy, University of Cambridge, Madingley Road, Cambridge, CB3 0HA, UK
  index: 4

date: 5 July 2018
bibliography: paper.bib
---

# Summary
HiPS (Hierarchical Progressive Surveys) [@2015A&A...578A.114F] is built upon the HEALPix framework and provides a way to store large astronomical survey sky images and catalog datasets on servers (such as HiPS at CDS  (\url{http://aladin.u-strasbg.fr/hips}), that allows clients to efficiently fetch only the image tiles or catalog parts for a given region of the sky they are interested in.

Currently, there are clients built using HiPS, such as Aladin and Aladin Lite (\url{http://aladin.u-strasbg.fr/aladin.gml}) but they are written in Java and JavaScript, respectively. There is also ipyaladin, which provides a bridge between Jupyter and Aladin Lite, and enables interactive sky visualization in IPython notebooks.

## Scope of the Package
The `hips` package provides flexibility by extending both a high-level and low-level API for novice and advanced users, respectively. It provides the functionality for drawing a sky image from HiPS tiles, transforming HiPS to WCS images, and HEALPix to HiPS. Additional features include progress bar reporting, asynchronous tile fetching, and support for multiple image formats.

For a more comprehensive introduction to the package, please see the documentation at (\url{http://hips.readthedocs.io}) and the source code at (\url{http://github.com/hipspy/hips}).

## Tile Drawing Algorithm
Projective transformation is applied for projecting HiPS tiles onto the sky image. To achieve this, we first compute the tile corners, which helps us in determining the position where the tile is to be placed. The tiles are further split into four children tiles, which is done to fix the tile distortion issue, and results in a more precise image.

# Example Usage
A sky image from HiPS image tiles can be drawn with the `hips` package, following these three steps:

1. Specify the sky image geometry you want by creating a `WCSGeometry` object:
	```python
	from astropy.coordinates import SkyCoord
	from hips import WCSGeometry

	geometry = WCSGeometry.create(
	     skydir=SkyCoord(0, 0, unit='deg', frame='galactic'),
	     width=2000, height=1000, fov="3 deg",
	     coordsys='galactic', projection='AIT',
	)
	```
2. Specify the HiPS survey by providing a valid HiPS survey ID:
	```python
	hips_survey = 'CDS/P/DSS2/red'
	```
3. Call the [`make_sky_image`](https://hips.readthedocs.io/en/latest/api/hips.make_sky_image.html#hips.make_sky_image "hips.make_sky_image") function to fetch the HiPS data and draw it, returning an object of [`HipsDrawResult`](https://hips.readthedocs.io/en/latest/api/hips.HipsDrawResult.html#hips.HipsDrawResult "hips.HipsDrawResult"). By default a progress bar is shown for fetching and drawing HiPS tiles. For batch processing, this can be turned off by passing a keyword argument: `progress_bar=False`:
	```python
	from hips import make_sky_image
	result = make_sky_image(geometry, hips_survey, 'png')
	```
This procedure produces the following image:

![all-sky-imge](plot_jpg.hires.png)

# Acknowledgements
This project was initiated as part of Google Summer of Code 2017 program (\url{https://summerofcode.withgoogle.com}) under the Open Astronomy umbrella organization. The authors would like to thank Google for hosting this program. We gratefully acknowledge Astropy for their affiliated packages which are extensively used in this package.

# References
