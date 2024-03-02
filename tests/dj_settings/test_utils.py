from __future__ import annotations

from pathlib import Path

import pytest

from dj_settings import utils
from dj_settings.types import SupportedType


@pytest.mark.parametrize(
    ("filename", "same_suffix", "expected_paths"),
    [
        (".env", False, [Path(".env.d/.env.01")]),
        (
            "override.toml",
            True,
            [
                Path("override.toml"),
                Path("override.toml.d/01-this.toml"),
                Path("override.toml.d/02-that.toml"),
            ],
        ),
    ],
)
def test_get_override_paths(
    data_dir: Path, filename: str, same_suffix: bool, expected_paths: list[Path]
) -> None:
    env_path = data_dir.joinpath(filename)
    expected_paths = [
        data_dir.joinpath(expected_path) for expected_path in expected_paths
    ]
    assert (
        list(utils.get_override_paths(env_path, same_suffix=same_suffix))
        == expected_paths
    )


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


@pytest.mark.parametrize(
    ("path", "force_type", "expected"),
    [
        (Path("settings.ini"), None, "ini"),
        (Path("settings.ini"), "toml", "toml"),
        (Path(".env"), None, "env"),
        (Path(".env"), "json", "json"),
    ],
)
def test_get_type(
    path: Path, force_type: SupportedType | None, expected: SupportedType
) -> None:
    assert utils.get_type(path, force_type) == expected


def test_extract_data(data_dir: Path) -> None:
    path = data_dir.joinpath("settings.toml")
    assert utils.extract_data(path, "toml") == {
        "database": {"username": "aria.stark", "password": "valar morghulis"}
    }
