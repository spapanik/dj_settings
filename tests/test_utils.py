from pathlib import Path

from dj_settings import utils


def test_include():
    path = Path(__file__)
    utils.include(path.parent.joinpath("data", "vars.py"))
    assert lowercase == 1  # noqa: F821
    assert UPPERCASE == 2  # noqa: F821
