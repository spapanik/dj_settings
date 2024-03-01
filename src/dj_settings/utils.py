from __future__ import annotations

import json
import os
from configparser import RawConfigParser
from itertools import chain
from pathlib import Path
from typing import Any, Iterable, Iterator, cast

import yaml

from dj_settings._seven import toml_parser
from dj_settings.constants import ETC, HOME_CONF, SUPPORTED_TYPES
from dj_settings.exceptions import SectionError
from dj_settings.types import ConfDict, SupportedType


class SettingsParser:
    __slots__ = ["path", "type", "_data"]

    def __init__(self, path: str | Path, force_type: SupportedType | None = None):
        self.path = Path(path)
        self.type = get_type(self.path, force_type)
        self._data: ConfDict | None = None

    @property
    def data(self) -> ConfDict:
        if self._data is None:
            self._data = {}
            for path in get_override_paths(self.path, self.type):
                self._data = deep_merge(self._data, extract_data(path, self.type))
        return self._data

    def extract_value(self, name: str, sections: Iterable[Any]) -> Any:
        data = self.data
        for section in chain(sections, [name]):
            try:
                data = data[section]
            except (KeyError, AttributeError) as exc:  # noqa: PERF203
                msg = "Missing section"
                raise SectionError(msg) from exc

        return data


def get_override_paths(path: Path, s_type: SupportedType) -> Iterator[Path]:
    if path.is_file() and os.access(path, os.R_OK):
        yield path

    suffix = path.suffix
    override_dir = path.with_suffix(f"{suffix}.d")
    if override_dir.is_dir():
        glob = ".env*" if s_type == "env" else f"*{suffix}"
        for path in sorted(override_dir.glob(glob)):
            if path.is_file() and os.access(path, os.R_OK):
                yield path


def deep_merge(dict_1: ConfDict, dict_2: ConfDict) -> ConfDict:
    output = dict_1.copy()
    for key, value in dict_2.items():
        if isinstance(dict_1.get(key), dict) and isinstance(value, dict):
            output[key] = deep_merge(dict_1[key], value)
        else:
            output[key] = value
    return output


def _get_config_paths(filename: Path, base_dir: Path | None) -> Iterator[Path]:
    if base_dir is not None:
        yield base_dir.joinpath(filename)
    yield HOME_CONF.joinpath(filename)
    yield ETC.joinpath(filename)


def get_config_paths(filename: Path, *, base_dir: Path | None = None) -> Iterator[Path]:
    for path in _get_config_paths(filename, base_dir=base_dir):
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


def setting(
    name: str,
    *,
    allow_env: bool = True,
    base_dir: str | Path | None = None,
    filename: str | Path | None = None,
    sections: Iterable[Any] = (),
    rtype: type = str,
    default: Any = None,
) -> Any:
    if allow_env and os.getenv(name) is not None:
        return rtype(os.environ[name])

    if filename is not None:
        if base_dir is not None:
            base_dir = Path(base_dir)
        for path in get_config_paths(Path(filename), base_dir=base_dir):
            parser = SettingsParser(path)
            try:
                value = parser.extract_value(name, sections)
            except SectionError:
                pass
            else:
                return rtype(value)

    return default
