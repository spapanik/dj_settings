from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    import tomllib

    toml_parser = tomllib.load
else:
    import tomli

    toml_parser = tomli.load
