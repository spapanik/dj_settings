# Installation

## Requirements

- **Python**: 3.11 or higher
- **Dependencies**: Automatically installed (pyutilkit and ruamel-yaml)

## Installation Methods

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is an extremely fast Python package installer and resolver.

```bash
uv pip install dj_settings
```

### Using pip

```bash
pip install dj_settings
```

### Using Poetry

```bash
poetry add dj_settings
```

### Using PEP 621 (pyproject.toml)

Add `dj_settings` to your project's dependencies in `pyproject.toml`:

```toml
[project]
dependencies = [
    "dj_settings>=9.0.0",
]
```

Then install with your preferred tool:

```bash
# With uv
uv sync

# With pip
pip install -e .

# With Poetry
poetry install
```

## Version Compatibility

| dj_settings Version | Python Version | Status |
|---------------------|----------------|--------|
| 9.x                 | ≥3.11          | Current |
| 8.x                 | ≥3.9           | Legacy  |
| 7.x                 | ≥3.9           | Legacy  |
| 6.x                 | ≥3.8           | Legacy  |
| 5.x                 | ≥3.7           | Legacy  |

For new projects, we recommend using the latest version (9.x) with Python 3.11+.

## Verifying Installation

After installation, verify that dj_settings is correctly installed:

```python
python -c "import dj_settings; print(dj_settings.__version__)"
```

This should print the installed version number.

## Next Steps

- Read the [Usage Guide](usage/index.md) to learn how to use dj_settings
- Check out the [Quick Start](README.md#quick-start) examples in the README
