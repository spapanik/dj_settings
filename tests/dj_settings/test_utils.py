import os
from pathlib import Path

import pytest

from dj_settings import utils


@pytest.mark.parametrize(["allow_env", "expected"], [[True, "env"], [False, "default"]])
def test_setting(allow_env, expected):
    os.environ["VAR"] = "env"
    assert utils.setting("VAR", allow_env=allow_env, default="default") == expected


class TestSettingsParser:
    @staticmethod
    @pytest.mark.parametrize(["suffix"], [[".ini"], [".json"], [".toml"], [".yaml"]])
    def test_data(suffix):
        file = Path(__file__).parents[1].joinpath("data/settings").with_suffix(suffix)
        assert utils.SettingsParser(file).data == {
            "database": {"username": "aria.stark", "password": "valar morghulis"}
        }
