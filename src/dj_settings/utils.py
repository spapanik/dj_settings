import json
import os
from configparser import ConfigParser
from itertools import chain
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, MutableMapping, Union, cast

PathConf = Union[str, Path, Dict[str, Any]]
ETC = Path("/etc/")
HOME_CONF = Path.home().joinpath(".config/")


class SectionError(KeyError):
    pass


class FileReader:
    __slots__ = ["path"]

    def __init__(self, path: Path):
        self.path = path

    @property
    def data(self) -> MutableMapping:
        suffix = self.path.suffix
        if suffix == ".json":
            with open(self.path) as file:
                return cast(Dict[str, Any], json.load(file))

        if suffix in (".conf", ".cfg", ".ini"):
            parser = ConfigParser()
            parser.read(self.path)
            return parser

        raise ValueError(f"{suffix} is not a supported extension (yet)")


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
