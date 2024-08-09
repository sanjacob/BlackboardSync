.. BlackboardSync documentation master file, created by
   sphinx-quickstart on Fri Mar  5 12:04:18 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Blackboard Sync
==========================================

.. image:: https://img.shields.io/github/license/sanjacob/BlackboardSync
    :target: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html


**BlackboardSync** is a multiplatform desktop application written in Python that automatically
downloads content from courses in your Blackboard account.

---------------

Features
--------

- Supported content:

  - Attachments of any type (e.g. .docx, .pptx, .pdf, etc.)
  - Internet links
  - Content descriptions (saved as html)

- Cross-platform

  - Linux, Windows, and macOS ready

Installation
------------

You can find all releases on GitHub_.
Only MacOS (.dmg) and Windows (.exe) are supported at the moment.

.. _GitHub: https://github.com/sanjacob/BlackboardSync/releases/


From PyPI
^^^^^^^^^

.. code-block:: bash

   $ python3 -m pip install blackboardsync
   $ python3 -m blackboard_sync # notice the underscore



API Documentation
-----------------

If you are interested about contributing, or if you just want
to understand the internals of BlackboardSync more.

.. toctree::
   :maxdepth: 2

   dev/bb_api
   dev/sync_api
   dev/qt_api
