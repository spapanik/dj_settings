# dj_settings: Project Settings the UNIX Way

[![build][build_badge]][build_url]
[![lint][lint_badge]][lint_url]
[![tests][tests_badge]][tests_url]
[![license][licence_badge]][licence_url]
[![codecov][codecov_badge]][codecov_url]
[![readthedocs][readthedocs_badge]][readthedocs_url]
[![pypi][pypi_badge]][pypi_url]
[![downloads][pepy_badge]][pepy_url]
[![build automation: yam][yam_badge]][yam_url]
[![Lint: ruff][ruff_badge]][ruff_url]

**dj_settings** provides a robust, UNIX-inspired approach to managing application configuration. It reads settings from multiple locations with a clear priority order, supporting environment variables, `.d` directory overrides, and multiple configuration formats.

Originally designed for Django projects, it has evolved into a versatile configuration management solution suitable for any Python application.

## Key Features

- **UNIX-style configuration hierarchy**: Read from `/etc/`, `~/.config/`, project directory, and environment variables
- **`.d` directory overrides**: Override configuration files with drop-in directories (e.g., `config.yml.d/*.yml`)
- **Multiple format support**: YAML, TOML, JSON, INI, and environment files
- **Type-safe settings classes**: Create typed configuration objects with decorators
- **Environment variable integration**: Seamlessly blend file-based and environment-based configuration
- **Array merging**: Optionally merge arrays instead of overwriting them

## Quick Start

```python
from pathlib import Path
from dj_settings import get_setting

# Get a setting with fallback chain
database_url = get_setting(
    "DATABASE_URL",
    use_env="DATABASE_URL",
    project_dir=Path("/path/to/project"),
    filename="config.yml",
    sections=["database"],
    default="sqlite:///db.sqlite3"
)
```

Or use type-safe settings classes:

```python
from pathlib import Path
from dj_settings import config_value, settings_class

@settings_class(project_dir=Path("/path/to/project"), filename="config.yml")
class Settings:
    debug: bool = config_value("DEBUG", use_env=True, default=False)
    database_url: str = config_value("DATABASE_URL", sections=["database"])
    allowed_hosts: list[str] = config_value(
        "ALLOWED_HOSTS",
        sections=["server"],
        merge_arrays=True,
        default=["localhost"]
    )

settings = Settings()
print(settings.debug)  # Type-safe access
```

## Documentation

- [Installation Guide](installation.md) - How to install dj_settings
- [Usage Guide](usage/index.md) - Comprehensive usage documentation
  - [Config Parsers](usage/parsers.md) - Using ConfigParser and get_setting
  - [Settings Classes](usage/decorator.md) - Type-safe settings with decorators
- [Changelog](CHANGELOG.md) - Version history and changes
- [License](LICENSE.md) - BSD-3-Clause license
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines

## Why dj_settings?

Managing configuration across different environments (development, staging, production) is challenging. dj_settings solves this by:

1. **Following UNIX conventions**: Uses the well-understood pattern of system-wide (`/etc/`), user-specific (`~/.config/`), and project-local configuration
2. **Supporting overrides**: The `.d` directory pattern allows incremental configuration without modifying base files
3. **Being format-agnostic**: Works with YAML, TOML, JSON, INI, and environment variables
4. **Providing type safety**: Modern Python type hints and dataclasses for better IDE support and error detection

[build_badge]: https://github.com/spapanik/dj_settings/actions/workflows/build.yml/badge.svg
[build_url]: https://github.com/spapanik/dj_settings/actions/workflows/build.yml
[lint_badge]: https://github.com/spapanik/dj_settings/actions/workflows/lint.yml/badge.svg
[lint_url]: https://github.com/spapanik/dj_settings/actions/workflows/lint.yml
[tests_badge]: https://github.com/spapanik/dj_settings/actions/workflows/tests.yml/badge.svg
[tests_url]: https://github.com/spapanik/dj_settings/actions/workflows/tests.yml
[licence_badge]: https://img.shields.io/pypi/l/dj_settings
[licence_url]: https://dj-settings.readthedocs.io/en/stable/LICENSE/
[codecov_badge]: https://codecov.io/github/spapanik/dj_settings/graph/badge.svg?token=Q20F84BW72
[codecov_url]: https://codecov.io/github/spapanik/dj_settings
[readthedocs_badge]: https://readthedocs.org/projects/dj-settings/badge/?version=latest
[readthedocs_url]: https://dj-settings.readthedocs.io/en/latest/
[pypi_badge]: https://img.shields.io/pypi/v/dj_settings
[pypi_url]: https://pypi.org/project/dj_settings
[pepy_badge]: https://pepy.tech/badge/dj_settings
[pepy_url]: https://pepy.tech/project/dj_settings
[yam_badge]: https://img.shields.io/badge/build%20automation-yamk-success
[yam_url]: https://github.com/spapanik/yamk
[ruff_badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
[ruff_url]: https://github.com/charliermarsh/ruff

[build_badge]: https://github.com/spapanik/dj_settings/actions/workflows/build.yml/badge.svg
[build_url]: https://github.com/spapanik/dj_settings/actions/workflows/build.yml
[lint_badge]: https://github.com/spapanik/dj_settings/actions/workflows/lint.yml/badge.svg
[lint_url]: https://github.com/spapanik/dj_settings/actions/workflows/lint.yml
[tests_badge]: https://github.com/spapanik/dj_settings/actions/workflows/tests.yml/badge.svg
[tests_url]: https://github.com/spapanik/dj_settings/actions/workflows/tests.yml
[licence_badge]: https://img.shields.io/pypi/l/dj_settings
[licence_url]: https://dj-settings.readthedocs.io/en/stable/LICENSE/
[codecov_badge]: https://codecov.io/github/spapanik/dj_settings/graph/badge.svg?token=Q20F84BW72
[codecov_url]: https://codecov.io/github/spapanik/dj_settings
[readthedocs_badge]: https://readthedocs.org/projects/dj-settings/badge/?version=latest
[readthedocs_url]: https://dj-settings.readthedocs.io/en/latest/
[pypi_badge]: https://img.shields.io/pypi/v/dj_settings
[pypi_url]: https://pypi.org/project/dj_settings
[pepy_badge]: https://pepy.tech/badge/dj_settings
[pepy_url]: https://pepy.tech/project/dj_settings
[yam_badge]: https://img.shields.io/badge/build%20automation-yamk-success
[yam_url]: https://github.com/spapanik/yamk
[ruff_badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
[ruff_url]: https://github.com/charliermarsh/ruff
[Documentation]: https://dj-settings.readthedocs.io/en/stable/
[Changelog]: https://dj-settings.readthedocs.io/en/stable/CHANGELOG/
