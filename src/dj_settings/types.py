from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Union

ConfDict = dict[str, Any]
PathConf = Union[str, Path, ConfDict]
SupportedType = Literal["json", "env", "yaml", "ini", "toml"]
