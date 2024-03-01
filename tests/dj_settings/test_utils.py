from __future__ import annotations

import pytest

from dj_settings import utils


@pytest.mark.parametrize(
    ("base", "override", "expected"),
    [
        ({"list": [1, 2, 3]}, {"list": [4, 5]}, {"list": [4, 5]}),
        (
            {"dict": {"x": 1, "y": 2}},
            {"dict": {"x": "a", "z": "b"}},
            {"dict": {"x": "a", "y": 2, "z": "b"}},
        ),
    ],
)
def test_deep_merge(
    base: dict[str, list[int]],
    override: dict[str, list[int]],
    expected: dict[str, list[int]],
) -> None:
    assert utils.deep_merge(base, override) == expected
