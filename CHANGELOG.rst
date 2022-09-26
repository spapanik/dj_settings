=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_, and this project adheres to `Semantic Versioning`_.

`Unreleased`_
-------------

Added
^^^^^
* Always return the settings in the order that they appear on the file
* Allow overriding the settings with a .d directory

`3.0.1`_ - 2022-05-03
---------------------

Fixed
^^^^^
* A typo that messed using .yml files as settings

`3.0.0`_ - 2022-05-01
---------------------

Added
^^^^^
* Expose FileReader and setting via the `__init__` module

Fixed
^^^^^
* /etc has the lowest priority and the current working directory has the highest

Changed
^^^^^^^
* Rename FileReader to SettingsParser
* Removed the default section from the ini settings parser

`2.1.0`_ - 2022-04-28
---------------------

Added
^^^^^
* Allow forcing the filetype

`2.0.0`_ - 2022-03-10
---------------------

Added
^^^^^
* Allow passing the path to the FileReader as a string

Changed
^^^^^^^
* .conf/.ini/.cfg files are parsed as python dictionaries

`1.0.0`_ - 2022-02-10
---------------------

Added
^^^^^
* Added yaml support

Changed
^^^^^^^
* Change toml parser to tomli

`0.4.0`_ - 2022-02-08
---------------------

Added
^^^^^
* Added toml support

`0.3.0`_ - 2022-01-10
---------------------

Removed
^^^^^^^
* Removed changelog from the published wheel

`0.2.0`_ - 2021-12-24
---------------------

Added
^^^^^
* Added python310 support

Removed
^^^^^^^
* Dropped python36 support
* Removed the ability to include python files for settings

`0.1.1`_ - 2021-08-13
---------------------

Added
^^^^^
* Allow getting the value from a single setting

`0.1.0`_ - 2020-07-01
---------------------

Added
^^^^^
* Allow including python files for settings


.. _`unreleased`: https://github.com/spapanik/dj_settings/compare/v3.0.1...main
.. _`3.0.1`: https://github.com/spapanik/dj_settings/compare/v3.0.0...v3.0.1
.. _`3.0.0`: https://github.com/spapanik/dj_settings/compare/v2.1.0...v3.0.0
.. _`2.1.0`: https://github.com/spapanik/dj_settings/compare/v2.0.0...v2.1.0
.. _`2.0.0`: https://github.com/spapanik/dj_settings/compare/v1.0.0...v2.0.0
.. _`1.0.0`: https://github.com/spapanik/dj_settings/compare/v0.4.0...v1.0.0
.. _`0.4.0`: https://github.com/spapanik/dj_settings/compare/v0.3.0...v0.4.0
.. _`0.3.0`: https://github.com/spapanik/dj_settings/compare/v0.2.0...v0.3.0
.. _`0.2.0`: https://github.com/spapanik/dj_settings/compare/v0.1.1...v0.2.0
.. _`0.1.1`: https://github.com/spapanik/dj_settings/compare/v0.1.0...v0.1.1
.. _`0.1.0`: https://github.com/spapanik/dj_settings/releases/tag/v0.1.0

.. _`Keep a Changelog`: https://keepachangelog.com/en/1.0.0/
.. _`Semantic Versioning`: https://semver.org/spec/v2.0.0.html
