=========================================
dj_settings: django settings the UNIX way
=========================================

.. image:: https://github.com/spapanik/dj_settings/actions/workflows/build.yml/badge.svg
  :alt: Build
  :target: https://github.com/spapanik/dj_settings/actions/workflows/build.yml
.. image:: https://img.shields.io/lgtm/alerts/g/spapanik/dj_settings.svg
  :alt: Total alerts
  :target: https://lgtm.com/projects/g/spapanik/dj_settings/alerts/
.. image:: https://img.shields.io/github/license/spapanik/dj_settings
  :alt: License
  :target: https://github.com/spapanik/dj_settings/blob/main/LICENSE.txt
.. image:: https://img.shields.io/pypi/v/dj_settings
  :alt: PyPI
  :target: https://pypi.org/project/dj_settings
.. image:: https://pepy.tech/badge/dj_settings
  :alt: Downloads
  :target: https://pepy.tech/project/dj_settings
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :alt: Code style
  :target: https://github.com/psf/black

``dj_settings`` offers way to add django settings in a way
that has been battle-tested for years in numerous UNIX apps,
reading from the value ``/etc/<conf_path>`` or ``~/.config//<conf_path>``
or ``<proj_path>/<conf_path>`` or an ``ENV VAR``, allowing overriding
from the next read location.

In a nutshell
-------------

Installation
^^^^^^^^^^^^

The easiest way is to use `poetry`_ to manage your dependencies and add *dj_settings* to them.

.. code-block:: toml

    [tool.poetry.dependencies]
    dj_settings = "^0.2.0"

Usage
^^^^^

``dj_settings`` will read from various config files to get the value of a variable,
in a way that's very familiar to all UNIX users. It allows setting default values,
and overriding with ENV VARs.


.. _poetry: https://python-poetry.org/


Links
-----

- `Documentation`_
- `Changelog`_


.. _Changelog: https://github.com/spapanik/dj_settings/blob/main/CHANGELOG.rst
.. _Documentation: https://dj-settings.readthedocs.io/en/latest/
