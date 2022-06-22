.. BlackboardSync documentation master file, created by
   sphinx-quickstart on Fri Mar  5 12:04:18 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

BlackboardSync
==========================================

.. image:: https://img.shields.io/github/license/jacobszpz/BlackboardSync
    :target: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html


**BlackboardSync** is a multiplatform desktop application written in Python that automatically
downloads content from courses in your Blackboard account.

---------------

Features
--------

- Supported content:

  - Attachments of any type (e.g. .docx, .pptx, .pdf, etc.)
  - Internet links
  - Content descriptions (saved as markdown files [1]_)

- Cross-platform

  - Linux, Windows, and macOS ready


.. [1]  List of `markdown editors`_. Personally, I like to use `Typora`_.


API Documentation
-----------------

Information about the internal APIs.

.. toctree::
   :maxdepth: 2

   dev/bb_api
   dev/sync_api
   dev/qt_api


Contributing
------------

If you intend to contribute to this project, this may be of interest.

.. toctree::
  :maxdepth: 2

  dev/bb_api


.. _Typora: https://typora.io
.. _markdown editors: https://www.markdownguide.org/tools/
