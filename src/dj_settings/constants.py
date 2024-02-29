from __future__ import annotations

from pathlib import Path
from typing import get_args

from dj_settings.types import SupportedType

ETC = Path("/etc/")
HOME_CONF = Path.home().joinpath(".config/")
SUPPORTED_TYPES = frozenset(get_args(SupportedType))
