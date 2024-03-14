# Usage

`dj_settings` will try to read a variable setting from the following
locations:

1. `/etc`
2. `${XDG_CONFIG_HOME}` (defaults to `~/.config`)
3. `PROJECT_BASE`
4. Environment variables
5. A default value (which itself defaults to None)

Also, following the UNIX tradition, if you have a settings file `/path/to/settings/config.extension`,
all the files with the same extensions that are in `/path/to/settings/config.extension.d/` will override
its values.

`dj_settings` exposes the following for public usage:

* `ConfigParser`, a class to parse settings file (with their overrides)
* `get_setting`, a method to parse a single setting
* `settings_class`, a decorator to create a settings class
* `config_value`, which represents an attribute of a settings class
