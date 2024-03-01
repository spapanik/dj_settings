from __future__ import annotations

import os
from pathlib import Path
from typing import get_args

from dj_settings.types import SupportedType

ETC = Path("/etc/")
HOME_CONF = Path(os.environ.get("XDG_CONFIG_HOME", Path.home().joinpath(".config/")))
SUPPORTED_TYPES = frozenset(get_args(SupportedType))
