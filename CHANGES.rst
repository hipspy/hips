
0.2
---

Version 0.2 of hips was released on October 28, 2017.

- Change from using ``healpy`` to ``astropy-healpix``.
  This means ``hips`` now works on Windows! [#109]
- Introduce asynchronous fetching of HiPS tiles [#106]
- Add progress bar support for fetching and drawing HiPS tiles [#105]
- Add reporting functionality for HipsPainter [#104]
- Fix tile splitting criterion [#101]

0.1
---

This first version of the hips package was released on July 28, 2017.
It contains a first implementation to fetch and draw tiles.

This is a very early release, to get some users and feedback.
Note that the API will change in the coming weeks,
and you can also expect new features, fixes and performance and usability enhancements.

The ``hips`` package started as a project developed as part of
Google summer of code 2017, i.e. planning in early 2017 and
coding in June 2017.
