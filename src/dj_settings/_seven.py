from __future__ import annotations

import sys

MINOR = sys.version_info.minor

if MINOR >= 10:  # noqa: PLR2004
    import inspect

    get_annotations = inspect.get_annotations

else:

    def get_annotations(cls: type) -> dict[str, object]:
        return cls.__annotations__


if MINOR >= 11:  # noqa: PLR2004
    import tomllib

    toml_parser = tomllib.load
else:
    import tomli

    toml_parser = tomli.load
