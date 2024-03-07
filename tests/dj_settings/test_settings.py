from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from dj_settings import settings


@pytest.fixture()
def config(data_dir: Path) -> Any:
    os.environ["USER"] = "Monsieur Madeleine"
    os.environ["AGE"] = "55"

    @settings.settings_class(project_dir=data_dir, filename="config.yml")
    class Settings:
        user: str = settings.settings_field("USER", allow_env=False, sections=["info"])
        email: str = settings.settings_field("email", sections=["info"])
        password: str = settings.settings_field(
            "PASSWORD", sections=["info"], default="super-secret-1234"
        )
        age: int = settings.settings_field("AGE", sections=["info"], rtype=int)

    return Settings()


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
        settings.get_setting(
            attribute,
            allow_env=allow_env,
            project_dir=data_dir,
            filename="config.yml",
            sections=["info"],
            default="default",
        )
        == expected
    )


@pytest.mark.parametrize(("allow_env", "expected"), [(True, "env"), (False, "default")])
def test_setting_without_file(allow_env: bool, expected: str) -> None:
    os.environ["VAR"] = "env"
    assert (
        settings.get_setting("VAR", allow_env=allow_env, default="default") == expected
    )


def test_settings_class(config: Any) -> None:
    assert config.user == "Jean Valjean"
    assert config.email == "madeleine@montreuil.gov"
    assert config.password == "super-secret-1234"  # noqa: S105
    assert config.age == 55


class TestSettingsParser:
    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data(data_dir: Path, suffix: str) -> None:
        file = data_dir.joinpath("settings").with_suffix(suffix)
        assert settings.SettingsParser([file]).data == {
            "database": {"username": "aria.stark", "password": "valar morghulis"}
        }

    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data_order(data_dir: Path, suffix: str) -> None:
        file = data_dir.joinpath("settings").with_suffix(suffix)
        database = settings.SettingsParser([file]).data["database"]
        assert list(database) == ["username", "password"]

    @staticmethod
    def test_overriding(data_dir: Path) -> None:
        file = data_dir.joinpath("override.toml")
        assert settings.SettingsParser([file]).data == {
            "foo": {"x": 100, "y": 20, "z": 3}
        }
