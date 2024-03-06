# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

### Added

- Added a @settings_class decorator to create settings classes

### Changed

- Moved SettingsParser and setting to a new module
- Renamed setting to get_setting
- SettingsParser now accepts a list of paths to parse

### Removed

- Dropped python 3.7 support

## [4.2.1] - 2023-02-28

### Fixed

- Fixed some type hints

## [4.2.0] - 2022-11-23

### Added

- Allowed parsing env files

## [4.1.0] - 2022-11-02

### Changed

- Removed the tomli dependency for versions that the standard library TOML parser is present

## [4.0.0] - 2022-09-26

### Added

- Made the settings to be returned in the order that they appear on the file
- Allowed overriding the settings with a .d directory

## [3.0.1] - 2022-05-03

### Fixed

- Fixed a typo that messed using .yml files as settings

## [3.0.0] - 2022-05-01

### Added

- Exposed FileReader and setting via the `__init__` module

### Fixed

- /etc has the lowest priority and the current working directory has the highest

### Changed

- Renamed FileReader to SettingsParser
- Removed the default section from the ini settings parser

## [2.1.0] - 2022-04-28

### Added

- Allowed forcing the filetype

## [2.0.0] - 2022-03-10

### Added

- Allowed passing the path to the FileReader as a string

### Changed

- .conf/.ini/.cfg files are now parsed as python dictionaries

## [1.0.0] - 2022-02-10

### Added

- Added yaml support

### Changed

- Changed toml parser to tomli

## [0.4.0] - 2022-02-08

### Added

- Added toml support

## [0.3.0] - 2022-01-10

### Removed

- Removed changelog from the published wheel

## [0.2.0] - 2021-12-24

### Added

- Added python310 support

### Removed

- Dropped python36 support
- Removed the ability to include python files for settings

## [0.1.1] - 2021-08-13

### Added

- Allowed getting the value from a single setting

## [0.1.0] - 2020-07-01

### Added

- Allowed including python files for settings


[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[Unreleased]: https://github.com/spapanik/dj_settings/compare/v4.2.1...main
[4.2.1]: https://github.com/spapanik/dj_settings/compare/v4.2.0...v4.2.1
[4.2.0]: https://github.com/spapanik/dj_settings/compare/v4.1.0...v4.2.0
[4.1.0]: https://github.com/spapanik/dj_settings/compare/v4.0.0...v4.1.0
[4.0.0]: https://github.com/spapanik/dj_settings/compare/v3.0.1...v4.0.0
[3.0.1]: https://github.com/spapanik/dj_settings/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/spapanik/dj_settings/compare/v2.1.0...v3.0.0
[2.1.0]: https://github.com/spapanik/dj_settings/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/spapanik/dj_settings/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/spapanik/dj_settings/compare/v0.4.0...v1.0.0
[0.4.0]: https://github.com/spapanik/dj_settings/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/spapanik/dj_settings/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/spapanik/dj_settings/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/spapanik/dj_settings/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/spapanik/dj_settings/releases/tag/v0.1.0
