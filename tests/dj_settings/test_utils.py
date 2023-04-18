from __future__ import annotations

import os
from pathlib import Path

import pytest

from dj_settings import utils


@pytest.mark.parametrize(("allow_env", "expected"), [(True, "env"), (False, "default")])
def test_setting(allow_env: bool, expected: str) -> None:
    os.environ["VAR"] = "env"
    assert utils.setting("VAR", allow_env=allow_env, default="default") == expected


class TestSettingsParser:
    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data(suffix: str) -> None:
        file = Path(__file__).parents[1].joinpath("data/settings").with_suffix(suffix)
        assert utils.SettingsParser(file).data == {
            "database": {"username": "aria.stark", "password": "valar morghulis"}
        }

    @staticmethod
    @pytest.mark.parametrize("suffix", [".ini", ".json", ".toml", ".yaml"])
    def test_data_order(suffix: str) -> None:
        file = Path(__file__).parents[1].joinpath("data/settings").with_suffix(suffix)
        database = utils.SettingsParser(file).data["database"]
        assert list(database) == ["username", "password"]

    @staticmethod
    def test_overriding() -> None:
        file = Path(__file__).parents[1].joinpath("data/override.toml")
        assert utils.SettingsParser(file).data == {
            "foo": {
                "x": 100,
                "y": 20,
                "z": 3,
            }
        }


@pytest.mark.parametrize(
    ("base", "override", "expected"),
    [
        ({"list": [1, 2, 3]}, {"list": [4, 5]}, {"list": [4, 5]}),
        (
            {"dict": {"x": 1, "y": 2}},
            {"dict": {"x": "a", "z": "b"}},
            {"dict": {"x": "a", "y": 2, "z": "b"}},
        ),
    ],
)
def test_deep_merge(
    base: dict[str, list[int]],
    override: dict[str, list[int]],
    expected: dict[str, list[int]],
) -> None:
    assert utils.deep_merge(base, override) == expected
