=====
Usage
=====

*dj_settings* will try to read a variable ``VAR`` from the following locations:

#. ``/etc/project.conf``
#. ``~/.config/project.conf``
#. ``BASE_DIR/project.conf``
#. Environment variable named ``VAR``

If the variable is defined in multiple locations it will choose the last one.

The recommended way to use it in a django project is to add the following lines
near the top of the settings file:

.. code-block:: python

    import pathlib
    from functools import partial

    from dj_settings.utils import setting

    BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
    project_setting = partial(
        setting,
        base_dir=BASE_DIR,
        filename="project.conf",
    )

in order to avoid passing the same arguments when using ``dj_settings``. When trying to get
the value of variable ``VAR`` defined in the section ``section`` of ``project.conf`` you can do

.. code-block:: python

    VAR = project_setting("VAR", sections=["section"], default="default")


Under the hood
--------------

.. py:module:: utils

Currently there is only the utils module, containing a single method, setting:

.. py:function:: setting( \
        name, \
        *, \
        allow_env = True, \
        base_dir = None, \
        filename = None, \
        sections = (), \
        rtype = str, \
        default = None, \
    )

   Retrieve a setting defined in a configuration file or an environment variable

   :param str name: The name of the variable
   :param bool allow_env: Whether the environment variable can be used to get the value
   :param Path base_dir: The base directory of the project
   :param Path filename: The config file's filename
   :param Iterable sections: The section that the value is defined in the config file
   :param type rtype: The type of the return value
   :param default: The default value to be returned
   :return: the value defined in one of the files or the default
