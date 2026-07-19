# Configuration Parsers

This guide covers the two primary ways to retrieve configuration values: the `ConfigParser` class for parsing entire configuration files, and the `get_setting` function for retrieving individual settings with fallback chains.

## ConfigParser Class

The `ConfigParser` class parses and merges multiple configuration files, automatically handling `.d` directory overrides.

### Basic Usage

```python
from pathlib import Path
from dj_settings import ConfigParser

# Parse multiple configuration files
parser = ConfigParser(
    paths=[
        Path("/etc/myapp.toml"),
        Path("/home/user/.config/myapp.yml")
    ]
)

# Access the merged configuration data
config_data = parser.data
print(config_data["database"]["host"])
```

### How It Works

When you provide paths to `ConfigParser`, it processes them in order:

1. For each base path (e.g., `/etc/myapp.toml`):
   - Reads the base file if it exists and is readable
   - Looks for a corresponding `.d` directory (e.g., `/etc/myapp.toml.d/`)
   - Merges all matching files from the `.d` directory in **alphabetical order**

2. Merges all configurations together, with later paths overriding earlier ones

Example file processing order:
```
/etc/myapp.toml                    # Base system config
/etc/myapp.toml.d/01-defaults.toml # System overrides
~/.config/myapp.yml                # User config
~/.config/myapp.yml.d/custom.yml   # User overrides
```

### Constructor Parameters

```python
ConfigParser(
    paths: Iterable[str | Path],      # Required: paths to config files
    force_type: SupportedType | None = None,  # Optional: force file type
    merge_arrays: bool = False        # Optional: merge lists instead of replacing
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `paths` | `Iterable[str \| Path]` | *Required* | List of configuration file paths to parse |
| `force_type` | `SupportedType \| None` | `None` | Force a specific parser type (`"yaml"`, `"toml"`, `"json"`, `"ini"`, `"env"`) |
| `merge_arrays` | `bool` | `False` | If `True`, concatenate arrays instead of replacing them |

### Properties and Methods

#### `data` Property

Returns the fully merged configuration as a dictionary. The parsing happens lazily on first access.

```python
parser = ConfigParser(paths=[Path("config.yml")])
config = parser.data  # Triggers parsing
print(config["app"]["name"])
```

#### `extract_value` Method

Extracts a specific value from the parsed configuration by navigating through sections.

```python
parser = ConfigParser(paths=[Path("config.yml")])

# Extract value from nested structure
# For config like: { "database": { "connection": { "url": "..." } } }
db_url = parser.extract_value("url", ["database", "connection"])

# Raises SectionError if path doesn't exist
try:
    value = parser.extract_value("missing", ["nonexistent", "path"])
except SectionError as e:
    print(f"Path not found: {e}")
```

**Parameters:**
- `name` (str): The final key to extract
- `sections` (Iterable[str]): List of section names to traverse

**Returns:** The value at the specified path

**Raises:** `SectionError` if any part of the path doesn't exist

### Advanced Examples

#### Using force_type

Force a specific parser regardless of file extension:

```python
# Parse a .txt file as YAML
parser = ConfigParser(
    paths=[Path("config.txt")],
    force_type="yaml"
)
```

#### Array Merging

Control how arrays are handled during merging:

```python
# config1.yml
plugins:
  - auth
  - logging

# config2.yml
plugins:
  - cache
  - metrics

# Without merge_arrays (default)
parser = ConfigParser(paths=[Path("config1.yml"), Path("config2.yml")])
print(parser.data["plugins"])  # ["cache", "metrics"]

# With merge_arrays=True
parser = ConfigParser(
    paths=[Path("config1.yml"), Path("config2.yml")],
    merge_arrays=True
)
print(parser.data["plugins"])  # ["auth", "logging", "cache", "metrics"]
```

---

## get_setting Function

The `get_setting` function retrieves a single configuration value with a complete fallback chain, checking environment variables, multiple config file locations, and finally using a default value.

### Basic Usage

```python
from pathlib import Path
from dj_settings import get_setting

# Simple usage with default
debug = get_setting("DEBUG", default=False)

# Full usage with all options
database_url = get_setting(
    "DATABASE_URL",
    use_env="DB_URL",              # Check DB_URL environment variable
    project_dir=Path("/myapp"),    # Look in /myapp/config.yml
    filename="config.yml",         # Config filename
    sections=["database"],         # Navigate to database section
    merge_arrays=False,            # Don't merge arrays
    rtype=str,                     # Return type
    default="sqlite:///db.sqlite3" # Fallback value
)
```

### Function Signature

```python
get_setting(
    name: str,                                    # Required: setting name
    *,
    use_env: bool | str = True,                  # Environment variable handling
    project_dir: str | Path | None = None,       # Project directory
    filename: str | Path | None = None,          # Config filename
    sections: Iterable[str] = (),                # Config sections to traverse
    merge_arrays: bool = False,                  # Array merging behavior
    rtype: Callable[[object], T] | type = str,  # Return type converter
    default: T | _Undefined = _UNDEFINED,        # Default value
) -> T
```

### Parameters

#### `name` (Required)

The name of the setting to retrieve. This serves two purposes:
1. As the key name when searching in configuration files
2. As the default environment variable name (when `use_env=True`)

```python
# Looks for "DATABASE_URL" in config and env var
get_setting("DATABASE_URL")
```

#### `use_env`

Controls environment variable checking:

| Value | Behavior |
|-------|----------|
| `True` | Check environment variable with same name as `name` |
| `str` | Check the specified environment variable name |
| `False` | Skip environment variable checking |

```python
# Check DEBUG env var
get_setting("debug", use_env=True)

# Check APP_DEBUG env var instead
get_setting("debug", use_env="APP_DEBUG")

# Don't check any env vars
get_setting("debug", use_env=False)
```

#### `project_dir`

The project directory where configuration files are located. When provided, dj_settings will look for `{project_dir}/{filename}` in addition to system and user config directories.

```python
# Looks in /myapp/config.yml, ~/.config/config.yml, /etc/config.yml
get_setting(
    "setting",
    project_dir=Path("/myapp"),
    filename="config.yml"
)
```

#### `filename`

The configuration filename to search for. If not provided, only environment variables are checked.

```python
# Only checks environment variables
get_setting("API_KEY", filename=None)

# Checks config files and environment variables
get_setting("API_KEY", filename="config.yml")
```

#### `sections`

A list of section names to traverse in the configuration file to reach the setting.

```python
# For config structure:
# database:
#   connection:
#     url: postgres://...

get_setting(
    "url",
    filename="config.yml",
    sections=["database", "connection"]
)
```

#### `merge_arrays`

If `True`, arrays in `.d` override files are concatenated instead of replaced.

```python
# Base config.yml
hosts:
  - localhost

# config.yml.d/override.yml
hosts:
  - example.com

# With merge_arrays=False (default)
result = get_setting("hosts", ..., merge_arrays=False)
# Result: ["example.com"]

# With merge_arrays=True
result = get_setting("hosts", ..., merge_arrays=True)
# Result: ["localhost", "example.com"]
```

#### `rtype`

A callable to convert the retrieved value to the desired type. Defaults to `str`.

```python
# Convert to integer
port = get_setting("PORT", rtype=int, default=8000)

# Convert to float
timeout = get_setting("TIMEOUT", rtype=float, default=30.5)

# Convert to boolean
debug = get_setting("DEBUG", rtype=lambda x: x.lower() == "true", default=False)

# Custom type conversion
from datetime import datetime
created = get_setting("CREATED", rtype=datetime.fromisoformat)
```

#### `default`

The fallback value if the setting is not found anywhere. If not provided and the setting is missing, a `TypeError` is raised.

```python
# With default value
value = get_setting("MISSING", default="fallback")

# Without default (raises TypeError if not found)
value = get_setting("REQUIRED_SETTING")  # May raise TypeError
```

### Return Value and Exceptions

**Returns:** The setting value converted to `rtype`

**Raises:**
- `TypeError`: If setting is not found and no default is provided

### Complete Example

```python
from pathlib import Path
from dj_settings import get_setting

# Application configuration
class AppConfig:
    @staticmethod
    def get_database_config():
        return {
            "url": get_setting(
                "DATABASE_URL",
                use_env="DATABASE_URL",
                project_dir=Path(__file__).parent,
                filename="config.yml",
                sections=["database"],
                default="sqlite:///dev.db"
            ),
            "pool_size": get_setting(
                "POOL_SIZE",
                use_env="DB_POOL_SIZE",
                project_dir=Path(__file__).parent,
                filename="config.yml",
                sections=["database"],
                rtype=int,
                default=5
            ),
            "debug_queries": get_setting(
                "DEBUG_QUERIES",
                use_env=True,
                project_dir=Path(__file__).parent,
                filename="config.yml",
                sections=["database", "options"],
                rtype=lambda x: x.lower() in ("true", "1", "yes"),
                default=False
            )
        }
```

### Error Handling

```python
from dj_settings.lib.exceptions import SectionError

# With a default: missing sections are silently handled
value = get_setting(
    "setting",
    filename="config.yml",
    sections=["nonexistent", "path"],
    default=None,
)
# Returns None rather than raising

# Without a default: missing setting raises TypeError
try:
    value = get_setting(
        "setting",
        filename="config.yml",
        sections=["nonexistent", "path"],
    )
except TypeError as e:
    print(f"Required setting not found: {e}")

# Use ConfigParser.extract_value directly if you need SectionError
parser = ConfigParser(paths=[Path("config.yml")])
try:
    value = parser.extract_value("setting", ["nonexistent", "path"])
except SectionError as e:
    print(f"Configuration path not found: {e}")
```

---

## Comparison: ConfigParser vs get_setting

| Feature | ConfigParser | get_setting |
|---------|--------------|-------------|
| Use Case | Parse entire config files | Get individual settings |
| Fallback Chain | No (only specified files) | Yes (env → system → user → project → default) |
| Environment Variables | No | Yes (optional) |
| Multiple Files | Yes | No (single filename) |
| Type Conversion | Manual | Built-in (`rtype`) |
| Lazy Loading | Yes (`data` property) | No (immediate) |
| Best For | Loading full configs | Getting specific settings |

## Next Steps

- Learn about [Settings Classes](decorator.md) for type-safe configuration objects
- Review the [Usage Overview](index.md) for configuration hierarchy details
