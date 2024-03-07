from __future__ import annotations

import sys

MINOR = sys.version_info.minor

if MINOR >= 10:
    import inspect

    get_annotations = inspect.get_annotations

else:
    from typing import Any

    def get_annotations(cls: type) -> dict[str, Any]:
        return cls.__annotations__


if MINOR >= 11:
    import tomllib

    toml_parser = tomllib.load
else:
    import tomli

    toml_parser = tomli.load
