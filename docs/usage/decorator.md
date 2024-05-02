## settings_classes

Another way to use `dj_settings` is to use it as a decorator to create a settings class.

```python
from dj_settings import config_value, settings_class


@settings_class(project_dir=Path("/path/to/project"), filename="config.yml")
class Settings:
    user: str = config_value("user", use_env=False, sections=["info"])
    email: str = config_value("email", use_env="EMAIL", sections=["info"])
    password: str = config_value("PASSWORD", sections=["info", "security"], default="super-secret")
    favourite_food: str = "bread"

settings = Settings()
```

This will create an object that will try to read from the following files for the attributes:

-   user
    1. `/etc/config.yml`, section `info`, attribute `user`
    2. `${XDG_CONFIG_HOME}/config.yml`, section `info`, attribute `user`
    3. `/path/to/project/config.yml`, section `info`, attribute `user`
    4. use `None`
-   email
    1. `/etc/config.yml`, section `info`, attribute `email`
    2. `${XDG_CONFIG_HOME}/config.yml`, section `info`, attribute `email`
    3. `/path/to/project/config.yml`, section `info`, attribute `email`
    4. the env var `EMAIL`
    5. default to None
-   password
    1. `/etc/config.yml`, section `info`, subsection `security`, attribute `PASSWORD`
    2. `${XDG_CONFIG_HOME}/config.yml`, section `info`, subsection `security`, attribute `PASSWORD`
    3. `/path/to/project/config.yml`, section `info`, subsection `security`, attribute `PASSWORD`
    4. the env var `PASSWORD`
    5. default to `super-secret`
-   favourite_food
    1. default to `bread`
