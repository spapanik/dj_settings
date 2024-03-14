from __future__ import annotations

import json
import os
from configparser import RawConfigParser
from pathlib import Path
from typing import Iterator, cast

import yaml

from dj_settings._seven import toml_parser
from dj_settings.constants import ETC, HOME_CONF, SUPPORTED_TYPES
from dj_settings.types import ConfDict, SupportedType


def get_override_paths(path: Path, *, same_suffix: bool) -> Iterator[Path]:
    if path.is_file() and os.access(path, os.R_OK):
        yield path

    suffix = path.suffix
    override_dir = path.with_suffix(f"{suffix}.d")
    if override_dir.is_dir():
        glob = f"*{suffix}" if same_suffix else f"{path.stem}*"
        for path in sorted(override_dir.glob(glob)):
            if path.is_file() and os.access(path, os.R_OK):
                yield path


def deep_merge(*dictionaries: ConfDict, merge_arrays: bool = False) -> ConfDict:
    output = dictionaries[0].copy()
    for dictionary in dictionaries[1:]:
        for key, value in dictionary.items():
            if isinstance(output.get(key), dict) and isinstance(value, dict):
                output[key] = deep_merge(output[key], value)
            elif (
                merge_arrays
                and isinstance(output.get(key), list)
                and isinstance(value, list)
            ):
                output[key] = output[key] + value
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


def extract_data(path: Path, settings_type: SupportedType) -> ConfDict:
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
            return cast(ConfDict, json.load(file))

    if settings_type == "ini":
        parser = RawConfigParser(default_section=None)  # type: ignore[call-overload]
        parser.optionxform = lambda option: option
        parser.read(path)
        return {key: dict(value) for key, value in parser.items() if key is not None}

    if settings_type == "toml":
        with path.open("rb") as binary_file:
            return toml_parser(binary_file)

    with path.open() as file:
        return cast(ConfDict, yaml.safe_load(file))
