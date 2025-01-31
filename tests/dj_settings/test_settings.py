from __future__ import annotations

import os
from typing import TYPE_CHECKING, Protocol

import pytest

from dj_settings import settings

if TYPE_CHECKING:
    from pathlib import Path


class Config(Protocol):
    user: str
    email: str
    password: str
    age: int
    favourite_food: str


@pytest.fixture
def config(data_dir: Path) -> Config:
    os.environ["USER"] = "Monsieur Madeleine"
    os.environ["AGE"] = "55"

    @settings.settings_class(project_dir=data_dir, filename="config.yml")
    class Settings:
        user: str = settings.config_value("USER", use_env=False, sections=["info"])
        email: str = settings.config_value("email", sections=["info"])
        password: str = settings.config_value(
            "PASSWORD", sections=["info"], default="super-secret-1234"
        )
        age: int = settings.config_value("AGE", sections=["info"], rtype=int)
        favourite_food: str = "bread"

    return Settings()


@pytest.mark.parametrize(
    ("attribute", "use_env", "expected"),
    [
        ("USER", True, "Monsieur Madeleine"),
        ("USER", False, "Jean Valjean"),
        ("email", True, "madeleine@montreuil.gov"),
        ("email", False, "madeleine@montreuil.gov"),
    ],
)
def test_setting(data_dir: Path, attribute: str, use_env: bool, expected: str) -> None:
    os.environ["USER"] = "Monsieur Madeleine"
    assert (
        settings.get_setting(
            attribute,
            use_env=use_env,
            project_dir=data_dir,
            filename="config.yml",
            sections=["info"],
            default="default",
        )
        == expected
    )


@pytest.mark.parametrize(
    ("use_env", "expected"),
    [(True, "env"), ("ANOTHER_VAR", "another_env"), (False, "default")],
)
def test_setting_without_file(use_env: bool | str, expected: str) -> None:
    os.environ["VAR"] = "env"
    os.environ["ANOTHER_VAR"] = "another_env"
    assert settings.get_setting("VAR", use_env=use_env, default="default") == expected


def test_setting_without_directory() -> None:
    assert settings.get_setting("VARIABLE", filename="missing_file.toml") is None


def test_settings_class(config: Config) -> None:
    assert config.user == "Jean Valjean"
    assert config.email == "madeleine@montreuil.gov"
    assert config.password == "super-secret-1234"  # noqa: S105
    assert config.age == 55
    assert config.favourite_food == "bread"


class TestConfigParser:
    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data(data_dir: Path, suffix: str) -> None:
        file = data_dir.joinpath("settings").with_suffix(suffix)
        assert settings.ConfigParser([file]).data == {
            "database": {"username": "aria.stark", "password": "valar morghulis"}
        }

    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data_order(data_dir: Path, suffix: str) -> None:
        file = data_dir.joinpath("settings").with_suffix(suffix)
        database: dict[str, str] = settings.ConfigParser([file]).data["database"]
        assert list(database) == ["username", "password"]

    @staticmethod
    def test_overriding(data_dir: Path) -> None:
        file = data_dir.joinpath("override.toml")
        parser = settings.ConfigParser([file])
        read_1 = parser.data
        read_2 = parser.data
        assert read_1 == {"foo": {"x": 100, "y": 20, "z": 3}}
        assert read_1 == read_2
