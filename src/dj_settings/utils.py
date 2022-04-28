import json
import os
from configparser import RawConfigParser
from itertools import chain
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Union, cast

import tomli
import yaml

PathConf = Union[str, Path, Dict[str, Any]]
ETC = Path("/etc/")
HOME_CONF = Path.home().joinpath(".config/")
SUPPORTED_TYPES = {"json", "ini", "toml", "yaml"}


class SectionError(KeyError):
    pass


class FileReader:
    __slots__ = ["path", "type"]

    def __init__(self, path: Union[str, Path], force_type: str = None):
        self.path = Path(path)
        self.type = self.get_type(force_type)
        if self.type not in SUPPORTED_TYPES:
            raise ValueError(f"{self.type} is not a supported extension (yet)")

    def get_type(self, force_type: str = None) -> str:
        if force_type is not None:
            return force_type

        suffix = self.path.suffix
        if suffix == ".json":
            return "json"
        if suffix in (".conf", ".cfg", ".ini"):
            return "ini"
        if suffix == ".toml":
            return "toml"
        if suffix in (".yaml", ".yml"):
            return "yaml"

        return None

    @property
    def data(self) -> Dict[str, Any]:
        if self.type == "json":
            with open(self.path) as file:
                return cast(Dict[str, Any], json.load(file))

        if self.type == "ini":
            parser = RawConfigParser()
            parser.optionxform = lambda option: option  # type: ignore
            parser.read(self.path)
            return {key: dict(value) for key, value in parser.items()}

        if self.type == "toml":
            with open(self.path, "rb") as binary_file:
                return tomli.load(binary_file)

        if self.type == "yaml":
            with open(self.path) as file:
                return cast(Dict[str, Any], yaml.safe_load(file))

        return None


def get_paths(filename: Path, *, base_dir: Path = None) -> Iterator[Path]:
    paths = [ETC.joinpath(filename), HOME_CONF.joinpath(filename)]
    if base_dir is not None:
        paths.append(base_dir.joinpath(filename))

    return filter(lambda path: os.access(path, os.R_OK), paths)


def extract_value(name: str, path: Path, sections: Iterable) -> Any:
    data = FileReader(path).data
    for section in chain(sections, [name]):
        try:
            data = data[section]
        except (KeyError, AttributeError):
            raise SectionError("Missing section")

    return data


def setting(
    name: str,
    *,
    allow_env: bool = True,
    base_dir: Union[str, Path] = None,
    filename: Union[str, Path] = None,
    sections: Iterable = (),
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
            except SectionError:
                pass
            else:
                return rtype(value)

    return default
