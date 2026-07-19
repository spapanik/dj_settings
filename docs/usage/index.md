# Usage Guide

## Configuration Hierarchy

`dj_settings` reads configuration values from multiple sources in a specific priority order. This allows you to set sensible defaults while enabling easy overrides for different environments.

### Read Order (Highest to Lowest Priority)

1. **Environment Variables** - When `use_env` is enabled
2. **System Config** - `/etc/{filename}`
3. **User Config** - `$XDG_CONFIG_HOME/{filename}` (defaults to `~/.config/`)
4. **Project Directory** - `{project_dir}/{filename}`
5. **Default Value** - Provided as fallback

Each configuration file can be overridden by files in its `.d` directory. For example, if you have `/etc/config.yml`, any YAML files in `/etc/config.yml.d/` will be merged on top, processed in alphabetical order.

### Example Configuration Flow

```
Environment Variable: DATABASE_URL=postgres://prod/db
                     ↓ (overrides if use_env=True)
System Config: /etc/config.yml
                     ↓ (merged with overrides from /etc/config.yml.d/)
User Config: ~/.config/config.yml
                     ↓ (merged with overrides from ~/.config/config.yml.d/)
Project Config: /myapp/config.yml
                     ↓ (merged with overrides from /myapp/config.yml.d/)
Default Value: "sqlite:///default.db"
```

## Public API

`dj_settings` provides four main components:

| Component | Type | Purpose |
|-----------|------|---------|
| [`ConfigParser`](parsers.md#configparser-class) | Class | Parse and merge multiple configuration files |
| [`get_setting`](parsers.md#get_setting-function) | Function | Retrieve a single setting with fallback chain |
| [`settings_class`](decorator.md) | Decorator | Create type-safe settings classes |
| [`config_value`](decorator.md#config_value-helper) | Helper | Define configurable attributes in settings classes |

## Supported Configuration Formats

dj_settings automatically detects and parses these formats based on file extension:

- **YAML**: `.yml`, `.yaml`
- **TOML**: `.toml`
- **JSON**: `.json`
- **INI/CFG**: `.ini`, `.cfg`, `.conf`
- **Environment Files**: `.env`, files starting with `.env`

## Quick Examples

### Simple Setting Retrieval

```python
from pathlib import Path
from dj_settings import get_setting

# Get a setting with full fallback chain
debug = get_setting(
    "DEBUG",
    use_env=True,  # Check DEBUG environment variable
    project_dir=Path("/myapp"),
    filename="config.yml",
    sections=["app"],
    default=False
)
```

### Using ConfigParser

```python
from pathlib import Path
from dj_settings import ConfigParser

# Parse multiple config files
parser = ConfigParser(
    paths=[
        Path("/etc/myapp.yml"),
        Path("/myapp/config.yml")
    ],
    merge_arrays=True  # Merge lists instead of replacing
)

# Access parsed data
data = parser.data
database_url = parser.extract_value("url", ["database"])
```

### Type-Safe Settings Class

```python
from pathlib import Path
from dj_settings import config_value, settings_class

@settings_class(project_dir=Path("/myapp"), filename="config.yml")
class AppSettings:
    debug: bool = config_value("DEBUG", use_env=True, default=False)
    database_url: str = config_value("DATABASE_URL", sections=["db"])
    workers: int = config_value("WORKERS", rtype=int, default=4)

settings = AppSettings()
print(settings.debug)  # Type-safe, IDE-supported
```

## Advanced Features

### The `.d` Override Pattern

Following UNIX conventions, any configuration file can be extended by a corresponding `.d` directory:

```
config.yml              # Base configuration
config.yml.d/
├── 01-database.yml     # Overrides applied first
├── 02-cache.yml        # Overrides applied second
└── 03-logging.yml      # Overrides applied third
```

Files in the `.d` directory are processed in **alphabetical order**, allowing you to control override precedence through naming.

### Array Merging

By default, arrays/lists in configuration files are replaced. Enable `merge_arrays=True` to concatenate them instead:

```python
# Base config.yml
allowed_hosts:
  - localhost

# config.yml.d/01-production.yml
allowed_hosts:
  - example.com
  - api.example.com

# With merge_arrays=False (default): ["example.com", "api.example.com"]
# With merge_arrays=True: ["localhost", "example.com", "api.example.com"]
```

### Environment Variable Integration

Control environment variable usage with the `use_env` parameter:

```python
# Use env var with same name as setting
get_setting("DEBUG", use_env=True)  # Checks DEBUG env var

# Use custom env var name
get_setting("debug_mode", use_env="APP_DEBUG")  # Checks APP_DEBUG env var

# Disable env var checking
get_setting("setting", use_env=False)  # Only checks config files
```

## Next Steps

- Learn about [ConfigParser and get_setting](parsers.md) for detailed API reference
- Explore [Settings Classes](decorator.md) for type-safe configuration
- Check out real-world examples in the [cookbook.yaml](../../cookbook.yaml) file
