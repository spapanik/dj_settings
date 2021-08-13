import json
import os
from configparser import ConfigParser
from importlib.util import module_from_spec, spec_from_file_location
from inspect import stack
from itertools import chain
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    MutableMapping,
    Tuple,
    Union,
    cast,
)

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


class Conf:
    __slots__ = ["path", "optional", "type"]

    def __init__(self, path_conf: PathConf):
        if not isinstance(path_conf, dict):
            path_conf = {"path": path_conf}

        path = path_conf["path"]
        if isinstance(path, str):
            path = Path(path).resolve()

        self.path: Path = path
        self.optional = path_conf.get("optional", False)
        self.type = self.path.suffix

    def items(self):
        parser = self.get_parser()
        yield from parser()

    def get_parser(self) -> Callable:
        if self.type == ".py":
            return self.parse_python

        raise ValueError("Not a supported type")

    def parse_python(self) -> Iterator[Tuple[str, Any]]:
        spec = spec_from_file_location(self.path.stem, self.path)
        if spec is None and not self.optional:
            raise ValueError("Not a valid path")

        module = module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        for var in dir(module):
            yield var, getattr(module, var)


def include(*paths: PathConf) -> None:
    frame = stack()[1].frame
    for path in paths:
        conf = Conf(path)
        for var, value in conf.items():
            frame.f_globals[var] = value
