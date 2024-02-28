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
from dj_settings.types import ConfDict


class SettingsParser:
    __slots__ = ["path", "type"]

    def __init__(self, path: str | Path, force_type: str = ""):
        self.path = Path(path)
        self.type = self.get_type(force_type)
        if self.type not in SUPPORTED_TYPES:
            msg = f"{self.type} is not a supported extension (yet)"
            raise ValueError(msg)

    def get_type(self, force_type: str = "") -> str:
        if force_type:
            return force_type

        suffix = self.path.suffix
        if suffix in {".conf", ".cfg", ".ini"}:
            return "ini"
        if suffix in {".yml", ".yaml"}:
            return "yaml"
        if suffix == ".toml":
            return "toml"
        if suffix == ".json":
            return "json"
        if self.path.name.startswith(".env"):
            return "env"
        msg = f"Cannot infer type of {self.path}"
        raise ValueError(msg)

    def _data(self) -> ConfDict:
        if self.type == "env":
            data = {}
            with self.path.open() as file:
                for raw_line in file:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, value = line.split("=")
                    data[key] = value
            return data

        if self.type == "json":
            with self.path.open() as file:
                return cast(ConfDict, json.load(file))

        if self.type == "ini":
            parser = RawConfigParser(default_section=None)  # type: ignore[call-overload]
            parser.optionxform = lambda option: option
            parser.read(self.path)
            return {
                key: dict(value) for key, value in parser.items() if key is not None
            }

        if self.type == "toml":
            with self.path.open("rb") as binary_file:
                return toml_parser(binary_file)

        if self.type == "yaml":
            with self.path.open() as file:
                return cast(ConfDict, yaml.safe_load(file))

        msg = "This is unreachable."
        raise RuntimeError(msg)

    @property
    def data(self) -> ConfDict:
        output = self._data()
        suffix = self.path.suffix
        override_dir = self.path.with_suffix(f"{suffix}.d")
        for path in sorted(override_dir.glob("*")):
            if self.type != "env" and path.suffix != suffix:
                continue
            output = deep_merge(output, type(self)(path).data)
        return output


def deep_merge(dict_1: ConfDict, dict_2: ConfDict) -> ConfDict:
    output = dict_1.copy()
    for key, value in dict_2.items():
        if isinstance(dict_1.get(key), dict) and isinstance(value, dict):
            output[key] = deep_merge(dict_1[key], value)
        else:
            output[key] = value
    return output


def get_paths(filename: Path, *, base_dir: Path | None = None) -> Iterator[Path]:
    paths = []
    if base_dir is not None:
        paths.append(base_dir.joinpath(filename))
    paths.extend([HOME_CONF.joinpath(filename), ETC.joinpath(filename)])

    return filter(lambda path: os.access(path, os.R_OK), paths)


def extract_value(name: str, path: Path, sections: Iterable[Any]) -> Any:
    data = SettingsParser(path).data
    for section in chain(sections, [name]):
        try:
            data = data[section]
        except (KeyError, AttributeError) as exc:  # noqa: PERF203
            msg = "Missing section"
            raise SectionError(msg) from exc

    return data


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
        paths = get_paths(Path(filename), base_dir=base_dir)
        for path in paths:
            try:
                value = extract_value(name, path, sections)
            except SectionError:  # noqa: PERF203
                pass
            else:
                return rtype(value)

    return default
