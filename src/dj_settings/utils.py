from importlib.util import module_from_spec, spec_from_file_location
from inspect import stack
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Tuple, Union

PathConf = Union[str, Path, Dict[str, Any]]


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
