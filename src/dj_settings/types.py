from __future__ import annotations

from typing import Any, Literal

ConfDict = dict[str, Any]
SupportedType = Literal["json", "env", "yaml", "ini", "toml"]
