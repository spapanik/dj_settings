from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from dj_settings import utils

if TYPE_CHECKING:
    from dj_settings.type_defs import SupportedType


@pytest.mark.parametrize(
    ("filename", "same_suffix", "expected_paths"),
    [
        (".env", False, [Path(".env.d/.env.01")]),
        (".env.test", False, [Path(".env.test"), Path(".env.test.d/.env.01")]),
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
    ("dictionaries", "merge_arrays", "expected"),
    [
        (({"list": [1]}, {"list": [2]}), True, {"list": [1, 2]}),
        (({"list": [1]}, {"list": [2]}), False, {"list": [2]}),
        (
            (
                {"dict": {"value_1": 1, "value_2": 2}},
                {},
                {"stray_key": "stray_value"},
                {"dict": {"value_1": 2, "value_3": 3}},
            ),
            False,
            {
                "dict": {"value_1": 2, "value_2": 2, "value_3": 3},
                "stray_key": "stray_value",
            },
        ),
        (
            (
                {"int_1": 1, "int_2": 1},
                {"int_1": 2, "int_3": 2},
                {"int_1": 3, "int_3": 3},
                {"int_1": 4, "int_4": 4},
            ),
            False,
            {"int_1": 4, "int_2": 1, "int_3": 3, "int_4": 4},
        ),
    ],
)
def test_deep_merge(
    dictionaries: tuple[dict[str, object], ...],
    merge_arrays: bool,
    expected: dict[str, object],
) -> None:
    assert utils.deep_merge(*dictionaries, merge_arrays=merge_arrays) == expected


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


def test_get_unsupported_type() -> None:
    with pytest.raises(ValueError, match="is not a supported extension"):
        utils.get_type(Path("settings.ini"), "unsupported")  # type: ignore[arg-type]


def test_get_non_inferrable_type() -> None:
    with pytest.raises(ValueError, match="Cannot infer type of"):
        utils.get_type(Path("settings.unsupported"))


def test_extract_data(data_dir: Path) -> None:
    path = data_dir.joinpath("settings.toml")
    assert utils.extract_data(path, "toml") == {
        "database": {"username": "aria.stark", "password": "valar morghulis"}
    }


def test_extract_data_from_env(data_dir: Path) -> None:
    path = data_dir.joinpath(".env.test")
    assert utils.extract_data(path, "env") == {"VARIABLE": "value"}
