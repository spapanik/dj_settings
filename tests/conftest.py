from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import pytest

from dj_settings.lib import utils


@pytest.fixture
def data_dir() -> Path:
    return Path(__file__).parent.joinpath("data")


@pytest.fixture(autouse=True)
def tiers(tmp_path: Path) -> Iterator[tuple[Path, Path]]:
    """Point the system and user tiers at empty temporary directories.

    Keeps the host's /etc and XDG_CONFIG_HOME out of every test, and gives
    tests that need tier files a place to create them.
    """
    etc = tmp_path.joinpath("etc")
    etc.mkdir()
    xdg = tmp_path.joinpath("xdg")
    xdg.mkdir()
    with (
        mock.patch.object(utils, "ETC", etc),
        mock.patch.object(utils, "HOME_CONF", xdg),
    ):
        yield etc, xdg
