.. include:: references.txt

.. _about:

*****
About
*****

Description
===========

HiPS (Hierarchical Progressive Surveys) is a way to store large
astronomical survey sky image and catalog datasets on servers (such as `HiPS at CDS`_),
that allows clients to efficiently fetch only the image tiles or catalog parts
for a given region of the sky they are interested in.
Similar to Google maps, but for astronomy (see the `HiPS paper`_).

This is a Python package to fetch and draw HiPS data.

It was just started in summer of 2017 and isn't stable or feature complete yet.
Feedback and contributions welcome!

Links
=====

* Code : https://github.com/hipspy/hips
* Docs : https://hips.readthedocs.io
* Contributors : https://github.com/hipspy/hips/graphs/contributors
* Releases: https://pypi.python.org/pypi/hips

Other resources
===============

* GSoC 2017 blog by Adeel: https://adl1995.github.io
* `HiPS at CDS`_ (contains a list and preview of available HiPS data)
* `HiPS paper`_
* `HiPS IVOA recommendation`_
* A Jupyter widget for Aladin Lite: https://github.com/cds-astro/ipyaladin
* Small example HiPS datasets we use for testing and docs examples: https://github.com/hipspy/hips-extra

(If you have a HiPS-related webpage or tool or resource you'd like mentioned here, let us know!)


Thanks
======

This package is being developed as part of Google Summer of Code 2017 program
by Adeel Ahmad, with Thomas Boch (CDS, Strasbourg) and Christoph Deil (MPIK, Heidelberg) as mentors.
We would like to thank Google, CDS, MPIK for their support!

If you're interested, you should follow Adeel's blog: https://adl1995.github.io/

Also: thanks to the Astropy team for developing and maintaining the
affiliated package-template and the ci-helpers! The recently introduced cookie-cutter
makes it even quicker to set up a new package like this one in a good, maintainable way.
