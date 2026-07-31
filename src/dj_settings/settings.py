from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import partial
from inspect import get_annotations
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from pyutilkit.classes import Singleton

from dj_settings.lib.exceptions import SettingNotFoundError
from dj_settings.lib.utils import (
    deep_merge,
    expand_stem,
    extract_data,
    get_override_paths,
    get_type,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from dj_settings.lib.type_defs import SupportedType


T = TypeVar("T")


class Sentinel(metaclass=Singleton):
    """Singleton class to represent an undefined value."""


UNDEFINED = Sentinel()


def _convert(value: object, rtype: Callable[[object], T] | type | Sentinel) -> T:
    if isinstance(rtype, Sentinel):
        return cast("T", value)
    return cast("T", rtype(value))


def _finalise(
    value: object,
    rtype: Callable[[object], T] | type | Sentinel,
    validator: Callable[[object], None] | None,
) -> T:
    converted = _convert(value, rtype)
    if validator is not None:
        validator(converted)
    return converted


def _derive_env_name(
    env_namespace: str | Sentinel, sections: Iterable[str], name: str
) -> str:
    namespace = "" if isinstance(env_namespace, Sentinel) else env_namespace
    prefix = [namespace] if namespace else []
    return "__".join(part.upper() for part in chain(prefix, sections, [name]))


class ConfigParser:
    __slots__ = ("_data", "_merge_arrays", "_paths")

    def __init__(
        self,
        *paths: str | Path,
        force_type: SupportedType | None = None,
        dir_namespace: str = "",
        merge_arrays: bool = False,
    ) -> None:
        self._paths: list[tuple[Path, SupportedType]] = []
        for path in paths:
            stem = Path(path)
            stem_type = get_type(stem, force_type)
            self._paths.extend(
                (tier_path, stem_type) for tier_path in expand_stem(stem, dir_namespace)
            )
        self._data: dict[str, Any] | None = None  # type: ignore[explicit-any]
        self._merge_arrays = merge_arrays

    @property
    def data(self) -> dict[str, Any]:  # type: ignore[explicit-any]
        if self._data is None:
            self._data = {}
            for base_path, base_type in self._paths:
                same_suffix = base_type != "env"
                for path in get_override_paths(base_path, same_suffix=same_suffix):
                    self._data = deep_merge(
                        self._data,
                        extract_data(path, base_type),
                        merge_arrays=self._merge_arrays,
                    )
        return self._data

    def get_setting(
        self,
        name: str,
        *,
        cli_value: T | Sentinel = UNDEFINED,
        use_env: bool | str = True,
        sections: Iterable[str] = (),
        env_namespace: str | Sentinel = UNDEFINED,
        rtype: Callable[[object], T] | type | Sentinel = UNDEFINED,
        default: T | Sentinel = UNDEFINED,
        validator: Callable[[object], None] | None = None,
    ) -> T:
        sections = tuple(sections)
        if not isinstance(env_namespace, Sentinel) and use_env is False:
            msg = "`env_namespace` is set, but reading the environment is disabled"
            raise ValueError(msg)

        if not isinstance(cli_value, Sentinel):
            return _finalise(cli_value, rtype, validator)
        layers = ["CLI: no value given"]

        if use_env is False:
            layers.append("environment: disabled")
        else:
            if isinstance(use_env, str):
                namespace = (
                    "" if isinstance(env_namespace, Sentinel) else env_namespace.upper()
                )
                env_var = "__".join(part for part in (namespace, use_env) if part)
            else:
                env_var = _derive_env_name(env_namespace, sections, name)
            env_value = os.getenv(env_var)
            if env_value is not None:
                return _finalise(env_value, rtype, validator)
            layers.append(f"environment: `{env_var}` is unset")

        path = [*sections, name]
        value: object = self.data
        try:
            for section in path:
                value = value[section]  # type: ignore[index]
        except (KeyError, TypeError):
            layers.append(f"files: section path `{'.'.join(path)}` not found")
        else:
            return _finalise(value, rtype, validator)

        if isinstance(default, Sentinel):
            layers.append("default: not provided")
            raise SettingNotFoundError(path, layers)
        return default


class _SettingsField(Generic[T]):
    __slots__ = (
        "cli_value",
        "default",
        "env_namespace",
        "name",
        "rtype",
        "sections",
        "use_env",
        "validator",
    )

    def __init__(
        self,
        name: str,
        *,
        cli_value: T | Sentinel,
        use_env: bool | str,
        sections: Iterable[str],
        env_namespace: str | Sentinel,
        rtype: Callable[[object], T] | type | Sentinel,
        default: T | Sentinel,
        validator: Callable[[object], None] | None,
    ) -> None:
        self.name = name
        self.cli_value = cli_value
        self.use_env = use_env
        self.sections = sections
        self.env_namespace = env_namespace
        self.rtype = rtype
        self.default = default
        self.validator = validator

    def resolve(self, parser: ConfigParser) -> T:
        return parser.get_setting(
            self.name,
            cli_value=self.cli_value,
            use_env=self.use_env,
            sections=self.sections,
            env_namespace=self.env_namespace,
            rtype=self.rtype,
            default=self.default,
            validator=self.validator,
        )


def config_value(  # type: ignore[explicit-any]
    name: str,
    *,
    cli_value: T | Sentinel = UNDEFINED,
    use_env: bool | str = True,
    sections: Iterable[str] = (),
    env_namespace: str | Sentinel = UNDEFINED,
    rtype: Callable[[object], T] | type | Sentinel = UNDEFINED,
    default: T | Sentinel = UNDEFINED,
    validator: Callable[[object], None] | None = None,
) -> Any:  # noqa: ANN401
    """Record how one settings-class field is resolved.

    It should only be used with a class decorated with the `settings_class` decorator.
    It returns Any, as the type should be set by the class.
    """
    return _SettingsField(
        name,
        cli_value=cli_value,
        use_env=use_env,
        sections=sections,
        env_namespace=env_namespace,
        rtype=rtype,
        default=default,
        validator=validator,
    )


def _preprocess_class(cls: type, parser: ConfigParser) -> type:
    for attribute in get_annotations(cls):
        value = getattr(cls, attribute, None)
        if isinstance(value, _SettingsField):
            setattr(
                cls, attribute, field(default_factory=partial(value.resolve, parser))
            )
    return cls


def settings_class(
    *paths: str | Path,
    force_type: SupportedType | None = None,
    dir_namespace: str = "",
    merge_arrays: bool = False,
) -> Callable[[type], type]:
    parser = ConfigParser(
        *paths,
        force_type=force_type,
        dir_namespace=dir_namespace,
        merge_arrays=merge_arrays,
    )

    def wrap(cls: type) -> type:
        cls = _preprocess_class(cls, parser)
        return dataclass(frozen=True, slots=True)(cls)

    return wrap
