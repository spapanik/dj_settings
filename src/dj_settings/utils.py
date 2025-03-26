from __future__ import annotations

import json
import os
from configparser import RawConfigParser
from typing import TYPE_CHECKING, Any, cast

from ruamel.yaml import YAML

from dj_settings._seven import toml_parser
from dj_settings.constants import ETC, HOME_CONF, SUPPORTED_TYPES

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from dj_settings.type_defs import SupportedType


def get_override_paths(path: Path, *, same_suffix: bool) -> Iterator[Path]:
    if path.is_file() and os.access(path, os.R_OK):
        yield path

    suffix = path.suffix
    override_dir = path.with_suffix(f"{suffix}.d")
    if override_dir.is_dir():
        glob = f"*{suffix}" if same_suffix else f"{path.stem}*"
        for override_path in sorted(override_dir.glob(glob)):
            if override_path.is_file() and os.access(override_path, os.R_OK):
                yield override_path


def deep_merge(
    *dictionaries: dict[str, object], merge_arrays: bool = False
) -> dict[str, object]:
    output = dictionaries[0].copy()
    for dictionary in dictionaries[1:]:
        for key, value in dictionary.items():
            if key not in output:
                output[key] = value
                continue
            current_value = output[key]
            if isinstance(current_value, dict) and isinstance(value, dict):
                output[key] = deep_merge(current_value, value)
            elif (
                merge_arrays
                and isinstance(current_value, list)
                and isinstance(value, list)
            ):
                output[key] = current_value + value
            else:
                output[key] = value
    return output


def _get_config_paths(filename: Path, project_dir: Path | None) -> Iterator[Path]:
    if project_dir is not None:
        yield project_dir.joinpath(filename)
    yield HOME_CONF.joinpath(filename)
    yield ETC.joinpath(filename)


def get_config_paths(
    filename: Path, *, project_dir: Path | None = None
) -> Iterator[Path]:
    for path in _get_config_paths(filename, project_dir=project_dir):
        if os.access(path, os.R_OK) and path.is_file():
            yield path


def get_type(path: Path, force_type: SupportedType | None = None) -> SupportedType:
    if force_type:
        if force_type not in SUPPORTED_TYPES:
            msg = f"{force_type} is not a supported extension (yet)"
            raise ValueError(msg)
        return force_type

    suffix = path.suffix
    if suffix in {".conf", ".cfg", ".ini"}:
        return "ini"
    if suffix in {".yml", ".yaml"}:
        return "yaml"
    if suffix == ".toml":
        return "toml"
    if suffix == ".json":
        return "json"
    if path.name.startswith(".env"):
        return "env"
    msg = f"Cannot infer type of {path}"
    raise ValueError(msg)


def extract_data(  # type: ignore[explicit-any]
    path: Path, settings_type: SupportedType
) -> dict[str, Any]:
    if settings_type == "env":
        data = {}
        with path.open() as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=")
                data[key] = value
        return data

    if settings_type == "json":
        with path.open() as file:
            return cast("dict[str, Any]", json.load(file))  # type: ignore[explicit-any]

    if settings_type == "ini":
        parser = RawConfigParser(default_section=None)  # type: ignore[call-overload]
        parser.optionxform = lambda option: option
        parser.read(path)
        return {key: dict(value) for key, value in parser.items() if key is not None}

    if settings_type == "toml":
        with path.open("rb") as binary_file:
            return toml_parser(binary_file)

    yaml = YAML(typ="safe")
    with path.open() as file:
        return cast("dict[str, Any]", yaml.load(file))  # type: ignore[explicit-any]
