# dj_settings: project settings the UNIX way

[![build][build_badge]][build_url]
[![lint][lint_badge]][lint_url]
[![tests][tests_badge]][tests_url]
[![license][licence_badge]][licence_url]
[![codecov][codecov_badge]][codecov_url]
[![readthedocs][readthedocs_badge]][readthedocs_url]
[![pypi][pypi_badge]][pypi_url]
[![downloads][pepy_badge]][pepy_url]
[![code style: black][black_badge]][black_url]
[![build automation: yam][yam_badge]][yam_url]
[![Lint: ruff][ruff_badge]][ruff_url]

`dj_settings` offers way to add project settings in a way that has been battle-tested for years
in numerous UNIX apps, reading from the value `/etc/<config_file>` or `~/.config/<config_file>` or
`/path/to/project/<config_file>` or an `ENV VAR`, allowing overriding from the next read location.
All of them allow overriding `/path/to/config/file.ext` with `/path/to/config/file.ext.d/<filename>.ext`.
It started by targeting django, but it has grown to be used as a general settings or config parser.

### Usage

`dj_settings` will read from various config files to get the value of a variable, in a way
that's very familiar to all UNIX users. It allows setting default values, and overriding
with ENV VARs and .d directories.

## Links

-   [Documentation]
-   [Changelog]

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
[black_badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black_url]: https://github.com/psf/black
[yam_badge]: https://img.shields.io/badge/build%20automation-yamk-success
[yam_url]: https://github.com/spapanik/yamk
[ruff_badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
[ruff_url]: https://github.com/charliermarsh/ruff
[Documentation]: https://dj-settings.readthedocs.io/en/stable/
[Changelog]: https://dj-settings.readthedocs.io/en/stable/CHANGELOG/
