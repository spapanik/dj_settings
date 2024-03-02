from __future__ import annotations

import os
from pathlib import Path

import pytest

from dj_settings import settings


@pytest.mark.parametrize(
    ("attribute", "allow_env", "expected"),
    [
        ("USER", True, "Monsieur Madeleine"),
        ("USER", False, "Jean Valjean"),
        ("email", True, "madeleine@montreuil.gov"),
        ("email", False, "madeleine@montreuil.gov"),
    ],
)
def test_setting(
    data_dir: Path, attribute: str, allow_env: bool, expected: str
) -> None:
    os.environ["USER"] = "Monsieur Madeleine"
    assert (
        settings.setting(
            attribute,
            allow_env=allow_env,
            base_dir=data_dir,
            filename="config.yml",
            sections=["info"],
            default="default",
        )
        == expected
    )


@pytest.mark.parametrize(("allow_env", "expected"), [(True, "env"), (False, "default")])
def test_setting_without_file(allow_env: bool, expected: str) -> None:
    os.environ["VAR"] = "env"
    assert settings.setting("VAR", allow_env=allow_env, default="default") == expected


class TestSettingsParser:
    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data(data_dir: Path, suffix: str) -> None:
        file = data_dir.joinpath("settings").with_suffix(suffix)
        assert settings.SettingsParser(file).data == {
            "database": {"username": "aria.stark", "password": "valar morghulis"}
        }

    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data_order(data_dir: Path, suffix: str) -> None:
        file = data_dir.joinpath("settings").with_suffix(suffix)
        database = settings.SettingsParser(file).data["database"]
        assert list(database) == ["username", "password"]

    @staticmethod
    def test_overriding(data_dir: Path) -> None:
        file = data_dir.joinpath("override.toml")
        assert settings.SettingsParser(file).data == {
            "foo": {"x": 100, "y": 20, "z": 3}
        }
