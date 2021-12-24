import os

import pytest

from dj_settings import utils


@pytest.mark.parametrize(["allow_env", "expected"], [[True, "env"], [False, "default"]])
def test_setting(allow_env, expected):
    os.environ["VAR"] = "env"
    assert utils.setting("VAR", allow_env=allow_env, default="default") == expected
