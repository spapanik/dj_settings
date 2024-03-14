# dj_settings: project settings the UNIX way

[![tests][test_badge]][test_url]
[![license][licence_badge]][licence_url]
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

- [Documentation]
- [Changelog]

[test_badge]: https://github.com/spapanik/dj_settings/actions/workflows/tests.yml/badge.svg
[test_url]: https://github.com/spapanik/dj_settings/actions/workflows/tests.yml
[licence_badge]: https://img.shields.io/badge/license-LGPL_v3-blue.svg
[licence_url]: https://github.com/spapanik/dj_settings/blob/main/docs/LICENSE.md
[pypi_badge]: https://img.shields.io/pypi/v/dj_settings
[pypi_url]: https://pypi.org/project/dj_settings
[pepy_badge]: https://pepy.tech/badge/dj_settings
[pepy_url]: https://pepy.tech/project/dj_settings
[black_badge]: https://img.shields.io/badge/code_style-black-000000.svg
[black_url]: https://github.com/psf/black
[yam_badge]: https://img.shields.io/badge/build_automation-yamk-success
[yam_url]: https://github.com/spapanik/dj_settings
[ruff_badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
[ruff_url]: https://github.com/charliermarsh/ruff
[Documentation]: https://dj-settings.readthedocs.io/en/stable/
[Changelog]: https://github.com/spapanik/dj_settings/blob/main/docs/CHANGELOG.md
