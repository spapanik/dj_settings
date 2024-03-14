from __future__ import annotations

import os
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Iterable

from dj_settings._seven import get_annotations
from dj_settings.exceptions import SectionError
from dj_settings.types import ConfDict, SupportedType
from dj_settings.utils import (
    deep_merge,
    extract_data,
    get_config_paths,
    get_override_paths,
    get_type,
)


class ConfigParser:
    __slots__ = ["_paths", "_data", "_merge_arrays"]

    def __init__(
        self,
        paths: Iterable[str | Path],
        force_type: SupportedType | None = None,
        *,
        merge_arrays: bool = False,
    ):
        self._paths = {Path(path): get_type(Path(path), force_type) for path in paths}
        self._data: ConfDict | None = None
        self._merge_arrays = merge_arrays

    @property
    def data(self) -> ConfDict:
        if self._data is None:
            self._data = {}
            for base_path, base_type in self._paths.items():
                same_suffix = base_type != "env"
                for path in get_override_paths(base_path, same_suffix=same_suffix):
                    self._data = deep_merge(
                        self._data,
                        extract_data(path, base_type),
                        merge_arrays=self._merge_arrays,
                    )
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
    use_env: bool | str = True,
    project_dir: str | Path | None = None,
    filename: str | Path | None = None,
    sections: Iterable[Any] = (),
    merge_arrays: bool = False,
    rtype: type = str,
    default: Any = None,
) -> Any:
    if use_env:
        env_var = name if use_env is True else use_env
        if os.getenv(env_var) is not None:
            return rtype(os.environ[env_var])

    if filename is not None:
        if project_dir is not None:
            project_dir = Path(project_dir)
        parser = ConfigParser(
            get_config_paths(Path(filename), project_dir=project_dir),
            merge_arrays=merge_arrays,
        )
        try:
            value = parser.extract_value(name, sections)
        except SectionError:
            pass
        else:
            return rtype(value)

    return default


class _SettingsField:
    __slots__ = ["name", "use_env", "sections", "merge_arrays", "rtype", "default"]

    def __init__(
        self,
        name: str,
        *,
        use_env: bool | str,
        sections: Iterable[Any],
        merge_arrays: bool,
        rtype: type,
        default: Any,
    ):
        self.name = name
        self.use_env = use_env
        self.sections = sections
        self.merge_arrays = merge_arrays
        self.rtype = rtype
        self.default = default

    def __call__(
        self, project_dir: Path | str | None, filename: Path | str | None
    ) -> Any:
        return get_setting(
            self.name,
            use_env=self.use_env,
            project_dir=project_dir,
            filename=filename,
            sections=self.sections,
            merge_arrays=self.merge_arrays,
            rtype=self.rtype,
            default=self.default,
        )


def config_value(
    name: str,
    *,
    use_env: bool | str = True,
    sections: Iterable[Any] = (),
    merge_arrays: bool = False,
    rtype: type = str,
    default: Any = None,
) -> Any:

    return _SettingsField(
        name,
        use_env=use_env,
        sections=sections,
        merge_arrays=merge_arrays,
        rtype=rtype,
        default=default,
    )


def _preprocess_class(
    cls: type, project_dir: Path | str | None, filename: Path | str | None
) -> type:
    for attribute in get_annotations(cls):
        value = getattr(cls, attribute, None)
        if isinstance(value, _SettingsField):
            setattr(cls, attribute, field(default=value(project_dir, filename)))
    return cls


def settings_class(
    project_dir: Path | str | None = None, filename: Path | str | None = None
) -> Callable[[type], type]:
    def wrap(cls: type) -> type:
        cls = _preprocess_class(cls, project_dir, filename)
        return dataclass(frozen=True)(cls)

    return wrap
