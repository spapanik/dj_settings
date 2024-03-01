from __future__ import annotations

import os
from pathlib import Path

import pytest

from dj_settings import settings


@pytest.mark.parametrize(("allow_env", "expected"), [(True, "env"), (False, "default")])
def test_setting(allow_env: bool, expected: str) -> None:
    os.environ["VAR"] = "env"
    assert settings.setting("VAR", allow_env=allow_env, default="default") == expected


class TestSettingsParser:
    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data(suffix: str) -> None:
        file = Path(__file__).parents[1].joinpath("data/settings").with_suffix(suffix)
        assert settings.SettingsParser(file).data == {
            "database": {"username": "aria.stark", "password": "valar morghulis"}
        }

    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data_order(suffix: str) -> None:
        file = Path(__file__).parents[1].joinpath("data/settings").with_suffix(suffix)
        database = settings.SettingsParser(file).data["database"]
        assert list(database) == ["username", "password"]

    @staticmethod
    def test_overriding() -> None:
        file = Path(__file__).parents[1].joinpath("data/override.toml")
        assert settings.SettingsParser(file).data == {
            "foo": {"x": 100, "y": 20, "z": 3}
        }
