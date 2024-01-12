# Usage

`dj_setting` will try to read a variable `VAR` from the following
locations:

1. `/etc/project.conf`
2. `~/.config/project.conf`
3. `BASE_DIR/project.conf`
4. Environment variable named `VAR`

If the variable is defined in multiple locations it will choose the last
one. Also, adding a `project.conf.d/` directory, will override the
settings in the respective project.conf file.

The recommended way to use it in a django project is to add the
following lines near the top of the settings file:

``` python
import pathlib
from functools import partial

from dj_settings import setting

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
project_setting = partial(
    setting,
    base_dir=BASE_DIR,
    filename="project.conf",
)
```

in order to avoid passing the same arguments when using `dj_settings`.
When trying to get the value of variable `VAR` defined in the section
`section` of `project.conf` you can do

``` python
VAR = project_setting("VAR", sections=["section"], default="default")
```
