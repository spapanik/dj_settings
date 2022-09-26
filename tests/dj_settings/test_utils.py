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


@pytest.mark.parametrize(
    ["base", "override", "expected"],
    [
        [{"list": [1, 2, 3]}, {"list": [4, 5]}, {"list": [4, 5]}],
        [
            {"dict": {"x": 1, "y": 2}},
            {"dict": {"x": "a", "z": "b"}},
            {"dict": {"x": "a", "y": 2, "z": "b"}},
        ],
    ],
)
def test_deep_merge(base, override, expected):
    assert utils.deep_merge(base, override) == expected
