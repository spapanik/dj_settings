# Installation

# Using uv

[uv] is an extremely fast Python package installer.
You can use it to install `dj_settings` and try it out:

```console
$ uv pip install dj_settings
```

# Using a PEP 621 compliant build backend

[PEP 621] is the standard way to store your dependencies in a `pyproject.toml` file.
You can add `dj_settings` to your `pyproject.toml` file:

```toml
[project]
dependencies = [
    "dj_settings~=5.0",
    ....
]
```

## Python Version Requirement

Please note that `dj_settings` requires Python 3.9 or higher. If you're not using uv,
please ensure that you have such a version installed in your system.

[uv]: https://github.com/astral-sh/uv
[PEP 621]: https://peps.python.org/pep-0621/
