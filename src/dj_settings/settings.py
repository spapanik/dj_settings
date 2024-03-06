from __future__ import annotations

import inspect
import os
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Iterable

from dj_settings.exceptions import SectionError
from dj_settings.types import ConfDict, SupportedType
from dj_settings.utils import (
    deep_merge,
    extract_data,
    get_config_paths,
    get_override_paths,
    get_type,
)


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
            same_suffix = self.type != "env"
            for path in get_override_paths(self.path, same_suffix=same_suffix):
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


def get_setting(
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


class SettingsField:
    __slots__ = ["name", "allow_env", "sections", "rtype", "default"]

    def __init__(
        self,
        name: str,
        *,
        allow_env: bool,
        sections: Iterable[Any],
        rtype: type,
        default: Any,
    ):
        self.name = name
        self.allow_env = allow_env
        self.sections = sections
        self.rtype = rtype
        self.default = default

    def __call__(self, base_dir: Path | str | None, filename: Path | str | None) -> Any:
        return get_setting(
            self.name,
            allow_env=self.allow_env,
            base_dir=base_dir,
            filename=filename,
            sections=self.sections,
            rtype=self.rtype,
            default=self.default,
        )


def settings_field(
    name: str,
    *,
    allow_env: bool = True,
    sections: Iterable[Any] = (),
    rtype: type = str,
    default: Any = None,
) -> Any:

    return SettingsField(
        name, allow_env=allow_env, sections=sections, rtype=rtype, default=default
    )


def _preprocess_class(
    cls: type, base_dir: Path | str | None, filename: Path | str | None
) -> type:
    for attribute in inspect.get_annotations(cls):
        value = getattr(cls, attribute, None)
        if isinstance(value, SettingsField):
            setattr(cls, attribute, field(default=value(base_dir, filename)))
    return cls


def settings_class(
    base_dir: Path | str | None = None, filename: Path | str | None = None
) -> Callable[[type], type]:
    def wrap(cls: type) -> type:
        cls = _preprocess_class(cls, base_dir, filename)
        return dataclass(frozen=True)(cls)

    return wrap
