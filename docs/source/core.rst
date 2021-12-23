=========================================
dj_settings: django settings the UNIX way
=========================================

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
    dj_settings = "^0.1.1"

Usage
^^^^^

``dj_settings`` will read from various config files to get the value of a variable,
in a way that's very familiar to all UNIX users. It allows setting default values,
and overriding with ENV VARs.


.. _poetry: https://python-poetry.org/
