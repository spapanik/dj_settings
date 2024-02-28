from __future__ import annotations

from pathlib import Path

ETC = Path("/etc/")
HOME_CONF = Path.home().joinpath(".config/")
SUPPORTED_TYPES = {"json", "ini", "toml", "yaml", "env"}
