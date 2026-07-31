from __future__ import annotations

import os
from typing import TYPE_CHECKING, Protocol, cast
from unittest import mock

import pytest

from dj_settings import settings
from dj_settings.lib import utils
from dj_settings.lib.exceptions import SettingNotFoundError

if TYPE_CHECKING:
    from pathlib import Path


class Config(Protocol):
    email: str
    age: int
    password: str
    favourite_food: str


class ConfigFactory(Protocol):
    def __call__(self, *, email: str) -> Config: ...


@pytest.fixture
def project_file(tmp_path: Path) -> Path:
    path = tmp_path.joinpath("project", "config.yml")
    path.parent.mkdir()
    path.write_text(
        "info:\n"
        "  email: madeleine@montreuil.gov\n"
        "  age: 55\n"
        "  hosts:\n"
        "    - localhost\n"
        "    - example.com\n"
    )
    return path


@pytest.fixture
def parser(project_file: Path) -> settings.ConfigParser:
    return settings.ConfigParser(project_file)


class TestConfigParser:
    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data(data_dir: Path, suffix: str) -> None:
        file = data_dir.joinpath("settings").with_suffix(suffix)
        assert settings.ConfigParser(file).data == {
            "database": {"username": "aria.stark", "password": "valar morghulis"}
        }

    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data_order(data_dir: Path, suffix: str) -> None:
        file = data_dir.joinpath("settings").with_suffix(suffix)
        database: dict[str, str] = settings.ConfigParser(file).data["database"]
        assert list(database) == ["username", "password"]

    @staticmethod
    def test_overriding(data_dir: Path) -> None:
        file = data_dir.joinpath("override.toml")
        parser = settings.ConfigParser(file)
        read_1 = parser.data
        read_2 = parser.data
        assert read_1 == {"foo": {"x": 100, "y": 20, "z": 3}}
        assert read_1 is read_2

    @staticmethod
    def test_tier_precedence(tiers: tuple[Path, Path], project_file: Path) -> None:
        etc, xdg = tiers
        etc.joinpath("config.yml").write_text("info:\n  email: root@etc\n  os: linux\n")
        xdg.joinpath("config.yml").write_text(
            "info:\n  email: user@xdg\n  shell: zsh\n"
        )
        assert settings.ConfigParser(project_file).data["info"] == {
            "email": "madeleine@montreuil.gov",
            "age": 55,
            "hosts": ["localhost", "example.com"],
            "os": "linux",
            "shell": "zsh",
        }

    @staticmethod
    def test_dir_namespace(tiers: tuple[Path, Path], tmp_path: Path) -> None:
        etc, _xdg = tiers
        etc.joinpath("config.yml").write_text("flat: true\n")
        etc.joinpath("tool").mkdir()
        etc.joinpath("tool", "config.yml").write_text("key: namespaced\n")
        stem = tmp_path.joinpath("project", "config.yml")
        assert settings.ConfigParser(stem, dir_namespace="tool").data == {
            "key": "namespaced"
        }

    @staticmethod
    def test_stem_major_merge(tiers: tuple[Path, Path], project_file: Path) -> None:
        etc, _xdg = tiers
        etc.joinpath("extra.yml").write_text("info:\n  email: system@etc\n")
        stems = settings.ConfigParser(project_file, project_file.with_name("extra.yml"))
        assert stems.data["info"]["email"] == "system@etc"

    @staticmethod
    def test_no_stems() -> None:
        assert settings.ConfigParser().data == {}


class TestGetSetting:
    @staticmethod
    @mock.patch.dict(os.environ, {"INFO__EMAIL": "env@example.com"})
    def test_cli_value_wins(parser: settings.ConfigParser) -> None:
        value = parser.get_setting(
            "email", cli_value="cli@example.com", sections=["info"]
        )
        assert value == "cli@example.com"

    @staticmethod
    def test_cli_value_is_coerced(parser: settings.ConfigParser) -> None:
        value: object = parser.get_setting("age", cli_value="66", rtype=int)
        assert value == 66

    @staticmethod
    @mock.patch.dict(os.environ, {"INFO__EMAIL": "env@example.com"})
    def test_env_name_derivation(parser: settings.ConfigParser) -> None:
        assert parser.get_setting("email", sections=["info"]) == "env@example.com"

    @staticmethod
    @mock.patch.dict(os.environ, {"APP__INFO__EMAIL": "namespaced@example.com"})
    def test_env_namespace_participates(parser: settings.ConfigParser) -> None:
        value: str = parser.get_setting("email", sections=["info"], env_namespace="app")
        assert value == "namespaced@example.com"

    @staticmethod
    @mock.patch.dict(os.environ, {"INFO__EMAIL": "env@example.com"})
    def test_empty_env_namespace_drops_namespace_only(
        parser: settings.ConfigParser,
    ) -> None:
        value: str = parser.get_setting("email", sections=["info"], env_namespace="")
        assert value == "env@example.com"

    @staticmethod
    def test_explicit_env_name_is_verbatim(parser: settings.ConfigParser) -> None:
        with mock.patch.object(
            os, "getenv", return_value="lower@example.com"
        ) as getenv:
            value: str = parser.get_setting(
                "email", use_env="dj_email", sections=["info"]
            )

        assert value == "lower@example.com"
        getenv.assert_called_once_with("dj_email")

    @staticmethod
    @mock.patch.dict(os.environ, {"DJANGO__USER": "arya"})
    def test_env_namespace_prefixes_explicit_env_name(
        parser: settings.ConfigParser,
    ) -> None:
        value: str = parser.get_setting(
            "username",
            sections=("database",),
            use_env="USER",
            env_namespace="DJANGO",
        )
        assert value == "arya"

    @staticmethod
    @mock.patch.dict(os.environ, {"INFO__EMAIL": "env@example.com"})
    def test_use_env_false_skips_environment(parser: settings.ConfigParser) -> None:
        value: str = parser.get_setting("email", use_env=False, sections=["info"])
        assert value == "madeleine@montreuil.gov"

    @staticmethod
    @mock.patch.dict(os.environ)
    def test_unset_variable_falls_through(parser: settings.ConfigParser) -> None:
        os.environ.pop("INFO__EMAIL", None)
        assert parser.get_setting("email", sections=["info"]) == (
            "madeleine@montreuil.gov"
        )

    @staticmethod
    def test_env_namespace_with_disabled_environment_raises(
        parser: settings.ConfigParser,
    ) -> None:
        with pytest.raises(ValueError, match="env_namespace"):
            parser.get_setting(
                "username",
                sections=("database",),
                use_env=False,
                env_namespace="DJANGO",
            )

    @staticmethod
    @mock.patch.dict(os.environ, {"INFO__AGE": "66"})
    def test_rtype_converts_env_value(parser: settings.ConfigParser) -> None:
        assert parser.get_setting("age", sections=["info"], rtype=float) == 66.0

    @staticmethod
    @mock.patch.dict(os.environ, {"INFO__AGE": "66"})
    def test_env_value_stays_a_string_without_rtype(
        parser: settings.ConfigParser,
    ) -> None:
        assert parser.get_setting("age", sections=["info"]) == "66"

    @staticmethod
    def test_file_value_keeps_parsed_type(parser: settings.ConfigParser) -> None:
        age: int = parser.get_setting("age", use_env=False, sections=["info"])
        hosts: list[str] = parser.get_setting("hosts", use_env=False, sections=["info"])
        assert age == 55
        assert hosts == ["localhost", "example.com"]

    @staticmethod
    def test_rtype_converts_file_value(parser: settings.ConfigParser) -> None:
        value: str = parser.get_setting(
            "age", use_env=False, sections=["info"], rtype=str
        )
        assert value == "55"

    @staticmethod
    def test_default_is_not_coerced(parser: settings.ConfigParser) -> None:
        value = parser.get_setting("missing", use_env=False, rtype=int, default="8000")
        assert value == "8000"

    @staticmethod
    @mock.patch.dict(os.environ, {"INFO__AGE": "66"})
    def test_validator_receives_coerced_value(parser: settings.ConfigParser) -> None:
        def validator(value: object) -> None:
            if not isinstance(value, int):
                msg = f"Expected an int, got {type(value).__name__}"
                raise TypeError(msg)

        value: int = parser.get_setting(
            "age", sections=["info"], rtype=int, validator=validator
        )
        assert value == 66

    @staticmethod
    def test_validator_raises(parser: settings.ConfigParser) -> None:
        def validator(value: object) -> None:
            msg = f"{value} is not acceptable"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="55 is not acceptable"):
            parser.get_setting(
                "age", use_env=False, sections=["info"], validator=validator
            )

    @staticmethod
    def test_validator_is_not_applied_to_default(
        parser: settings.ConfigParser,
    ) -> None:
        def validator(value: object) -> None:
            msg = f"{value} is not acceptable"
            raise ValueError(msg)

        value = parser.get_setting(
            "missing", use_env=False, default=None, validator=validator
        )
        assert value is None

    @staticmethod
    @mock.patch.dict(os.environ)
    def test_missing_setting_raises(parser: settings.ConfigParser) -> None:
        os.environ.pop("NONEXISTENT", None)
        with pytest.raises(SettingNotFoundError, match="nonexistent"):
            parser.get_setting("nonexistent")

    @staticmethod
    def test_missing_setting_raises_with_env_disabled(
        parser: settings.ConfigParser,
    ) -> None:
        with pytest.raises(SettingNotFoundError, match="nonexistent"):
            parser.get_setting("nonexistent", use_env=False)

    @staticmethod
    def test_section_path_into_scalar(parser: settings.ConfigParser) -> None:
        value = parser.get_setting(
            "years", use_env=False, sections=["info", "age"], default=0
        )
        assert value == 0

    @staticmethod
    def test_section_path_into_scalar_without_default(
        parser: settings.ConfigParser,
    ) -> None:
        with pytest.raises(SettingNotFoundError, match=r"info\.age\.years"):
            parser.get_setting("years", use_env=False, sections=["info", "age"])


class TestSettingsClass:
    @staticmethod
    @pytest.fixture
    def config(project_file: Path) -> Config:
        env = {"INFO__EMAIL": "env@example.com", "INFO__AGE": "66"}
        with mock.patch.dict(os.environ, env):

            @settings.settings_class(project_file)
            class Settings:
                email: str = settings.config_value("email", sections=["info"])
                age: int = settings.config_value(
                    "age", use_env=False, sections=["info"], rtype=int
                )
                password: str = settings.config_value(
                    "password", sections=["info"], default="super-secret-1234"
                )
                favourite_food: str = "bread"

            return Settings()

    @staticmethod
    def test_settings_class(config: Config) -> None:
        assert config.email == "env@example.com"
        assert config.age == 55
        assert config.password == "super-secret-1234"  # noqa: S105
        assert config.favourite_food == "bread"

    @staticmethod
    def test_resolution_happens_at_instantiation(project_file: Path) -> None:
        @settings.settings_class(project_file)
        class Settings:
            email: str = settings.config_value("email", sections=["info"])

        with mock.patch.dict(os.environ, {"INFO__EMAIL": "later@example.com"}):
            assert Settings().email == "later@example.com"
        with mock.patch.dict(os.environ):
            os.environ.pop("INFO__EMAIL", None)
            assert Settings().email == "madeleine@montreuil.gov"

    @staticmethod
    def test_constructor_overrides_field(project_file: Path) -> None:
        @settings.settings_class(project_file)
        class Settings:
            email: str = settings.config_value(
                "email", use_env=False, sections=["info"]
            )

        make_settings = cast("ConfigFactory", Settings)
        assert make_settings(email="override@example.com").email == (
            "override@example.com"
        )

    @staticmethod
    def test_missing_required_setting_raises_at_instantiation(
        project_file: Path,
    ) -> None:
        @settings.settings_class(project_file)
        class Settings:
            secret: str = settings.config_value(
                "secret", use_env=False, sections=["info"]
            )

        with pytest.raises(SettingNotFoundError, match=r"info\.secret"):
            Settings()

    @staticmethod
    def test_document_is_read_once_per_parser(project_file: Path) -> None:
        with mock.patch.object(
            settings, "extract_data", wraps=utils.extract_data
        ) as extract:

            @settings.settings_class(project_file)
            class Settings:
                email: str = settings.config_value(
                    "email", use_env=False, sections=["info"]
                )
                age: int = settings.config_value(
                    "age", use_env=False, sections=["info"], rtype=int
                )

            Settings()
            Settings()

        assert extract.call_count == 1
        assert extract.call_args.args[0] == project_file

    @staticmethod
    @mock.patch.dict(os.environ)
    def test_settings_class_without_files() -> None:
        os.environ.pop("TOKEN", None)

        @settings.settings_class()
        class Settings:
            token: str = settings.config_value("token", default="anonymous")

        assert Settings().token == "anonymous"  # noqa: S105
