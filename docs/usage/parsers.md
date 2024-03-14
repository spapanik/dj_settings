## parsers

One way to use `dj_settings` is to use it to parse config.

In order to parse any config class you can use the `ConfigParser`

``` python
from pathlib import Path

from dj_settings import ConfigParser

parser = ConfigParser(
    paths=(Path("/path/to/config_1.toml"), Path("/path/to/config_2.yml")),
)
```

This will parser and combine the following files in order:

1. `/path/to/config_1.toml`
2. `/path/to/config_1.toml.d/*.toml`
3. `/path/to/config_2.yml`
4. `/path/to/config_2.yml.d/*.yml`

The wildcards are parsed in alphabetical order.

Or you can use `get_setting` to get a single setting.

``` python
from dj_settings import get_setting

get_setting(
    "setting_name",
    use_env="NAME_AS_ENV_VAR",
    project_dir=Path("/path/to/project"),
    filename="config.json",
    sections=["section", "subsection"],
    merge_arrays=True,
    rtype=int,
    default=42,
)
```

The `setting_name` is the only required argument, and all the others are keyword arguments.

Their meaning is:

* use_env: if True, it will use the env_var with the same name as in the setting_name,
  if set to a string it will use this env_var,
  and if it's a False-y value it will ignore env_vars.
* project_dir: the path to the directory that the config file resides
  (in addition to `/etc` and `${XDG_CONFIG_HOME}`)
* filename: the filename of the config file (leave empty to only use env vars)
* sections: the sections of the config file to search for the setting
* merge_arrays: if set to True, arrays are merged, not overwritten
* rtype: the return type
* default: a default value
