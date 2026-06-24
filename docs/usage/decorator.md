# Settings Classes

Settings classes provide a type-safe, object-oriented approach to configuration management. By using the `@settings_class` decorator and `config_value` helper, you can define configuration schemas with full IDE support, type checking, and automatic value resolution.

## Overview

Settings classes combine the power of Python dataclasses with dj_settings' configuration resolution, giving you:

- **Type Safety**: Full type annotations with IDE autocomplete and static analysis support
- **Immutability**: Frozen dataclasses prevent accidental modification
- **Automatic Resolution**: Values are fetched from config files and environment variables at instantiation
- **Clean API**: Access settings as object attributes instead of string keys

## Basic Usage

```python
from pathlib import Path
from dj_settings import config_value, settings_class

@settings_class(project_dir=Path("/myapp"), filename="config.yml")
class AppSettings:
    # Simple setting with default
    debug: bool = config_value("DEBUG", use_env=True, default=False)

    # Setting from nested config section
    database_url: str = config_value(
        "DATABASE_URL",
        sections=["database", "connection"],
        default="sqlite:///db.sqlite3"
    )

    # Setting with custom env var name
    secret_key: str = config_value(
        "SECRET_KEY",
        use_env="APP_SECRET_KEY",
        default="change-me-in-production"
    )

    # Plain attribute (not from config)
    app_name: str = "My Application"

# Instantiate to resolve all values
settings = AppSettings()

# Access settings with full IDE support
if settings.debug:
    print(f"Connecting to {settings.database_url}")
```

## The @settings_class Decorator

The `@settings_class` decorator transforms a regular class into a frozen dataclass that automatically resolves configuration values during initialization.

### Signature

```python
settings_class(
    project_dir: Path | str | None = None,
    filename: Path | str | None = None
) -> Callable[[type], type]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_dir` | `Path \| str \| None` | `None` | Project directory for config file lookup |
| `filename` | `Path \| str \| None` | `None` | Configuration filename to search for |

### How It Works

When you instantiate a settings class, the decorator:

1. Scans all class attributes annotated with types
2. Identifies attributes assigned via `config_value()`
3. Resolves each `config_value` by calling `get_setting()` with the specified parameters
4. Replaces `config_value` objects with their resolved values
5. Converts the class to a frozen dataclass

### Example Config File Lookup

For a settings class defined as:

```python
@settings_class(project_dir=Path("/myapp"), filename="app.yml")
class Settings:
    value: str = config_value("setting")
```

The `value` attribute will be searched in this order:

1. Environment variable `setting` (if `use_env=True`)
2. `/myapp/app.yml` → section/path to `setting`
3. `~/.config/app.yml` → section/path to `setting`
4. `/etc/app.yml` → section/path to `setting`
5. Default value (if provided)

Each `.yml` file can be overridden by its corresponding `.yml.d/` directory.

---

## The config_value Helper

The `config_value()` function defines how a specific attribute should be resolved from configuration sources.

### Signature

```python
config_value(
    name: str,                                    # Required: setting name
    *,
    use_env: bool | str = True,                  # Environment variable handling
    sections: Iterable[str] = (),                # Config sections to traverse
    merge_arrays: bool = False,                  # Array merging behavior
    rtype: Callable[[object], T] | type = str,  # Return type converter
    default: T | _Undefined = _UNDEFINED,        # Default value
) -> Any
```

### Parameters

All parameters are identical to [`get_setting`](parsers.md#get_setting-function), as `config_value` internally uses `get_setting` to resolve values.

#### `name` (Required)

The key name to search for in configuration files.

```python
# Looks for "DATABASE_URL" in config
database_url: str = config_value("DATABASE_URL")
```

#### `use_env`

Controls environment variable checking:

```python
# Check env var with same name
debug: bool = config_value("DEBUG", use_env=True)

# Check custom env var name
api_key: str = config_value("API_KEY", use_env="MY_API_KEY")

# Disable env var checking
internal_flag: bool = config_value("FLAG", use_env=False)
```

#### `sections`

Navigate through nested configuration structures:

```python
# For YAML like:
# database:
#   primary:
#     host: localhost

host: str = config_value("host", sections=["database", "primary"])
```

#### `merge_arrays`

Control array merging behavior in `.d` overrides:

```python
# Merge arrays from override files
allowed_hosts: list[str] = config_value(
    "ALLOWED_HOSTS",
    sections=["server"],
    merge_arrays=True,
    default=["localhost"]
)
```

#### `rtype`

Convert values to specific types:

```python
# Integer conversion
port: int = config_value("PORT", rtype=int, default=8000)

# Float conversion
timeout: float = config_value("TIMEOUT", rtype=float, default=30.0)

# Boolean conversion
debug: bool = config_value(
    "DEBUG",
    rtype=lambda x: str(x).lower() in ("true", "1", "yes"),
    default=False
)

# List conversion
tags: list[str] = config_value(
    "TAGS",
    rtype=lambda x: x.split(",") if isinstance(x, str) else x,
    default=[]
)
```

#### `default`

Fallback value if the setting is not found:

```python
# With default
cache_ttl: int = config_value("CACHE_TTL", rtype=int, default=300)

# Without default (raises TypeError if missing)
required_secret: str = config_value("REQUIRED_SECRET")
```

---

## Advanced Patterns

### Multiple Configuration Files

Use different filenames for different settings groups:

```python
from pathlib import Path
from dj_settings import config_value, settings_class

# Database settings from db.yml
@settings_class(project_dir=Path("/myapp"), filename="db.yml")
class DatabaseSettings:
    url: str = config_value("URL", sections=["connection"])
    pool_size: int = config_value("POOL_SIZE", rtype=int, default=5)

# App settings from app.yml
@settings_class(project_dir=Path("/myapp"), filename="app.yml")
class AppSettings:
    debug: bool = config_value("DEBUG", use_env=True, default=False)
    secret_key: str = config_value("SECRET_KEY")

# Compose them
class Settings:
    db = DatabaseSettings()
    app = AppSettings()

settings = Settings()
print(settings.db.url)
print(settings.app.debug)
```

### Environment-Specific Settings

Leverage environment variables for environment-specific configuration:

```python
@settings_class(filename="config.yml")
class Settings:
    # Always check env var first
    environment: str = config_value(
        "ENVIRONMENT",
        use_env="APP_ENV",
        default="development"
    )

    # Different defaults based on environment
    debug: bool = config_value(
        "DEBUG",
        use_env=True,
        default=False  # Production-safe default
    )

    # Database URL from env or config
    database_url: str = config_value(
        "DATABASE_URL",
        use_env="DATABASE_URL",
        sections=["database"],
        default="sqlite:///dev.db"
    )

settings = Settings()

# In production: export APP_ENV=production DATABASE_URL=postgres://...
# In development: use config file defaults
```

### Nested Configuration Objects

Create hierarchical settings structures:

```python
@settings_class(filename="config.yml")
class DatabaseConfig:
    host: str = config_value("HOST", sections=["database"], default="localhost")
    port: int = config_value("PORT", sections=["database"], rtype=int, default=5432)
    name: str = config_value("NAME", sections=["database"], default="myapp")

    @property
    def url(self) -> str:
        return f"postgresql://{self.host}:{self.port}/{self.name}"

@settings_class(filename="config.yml")
class CacheConfig:
    backend: str = config_value("BACKEND", sections=["cache"], default="redis")
    ttl: int = config_value("TTL", sections=["cache"], rtype=int, default=300)

@settings_class(filename="config.yml")
class Settings:
    database: DatabaseConfig = None  # Will be set manually
    cache: CacheConfig = None

    def __post_init__(self):
        # Initialize nested configs
        self.database = DatabaseConfig()
        self.cache = CacheConfig()

settings = Settings()
print(settings.database.url)
print(settings.cache.backend)
```

### Validation and Post-Processing

Add validation logic to ensure configuration correctness:

```python
from dj_settings import config_value, settings_class

@settings_class(filename="config.yml")
class Settings:
    debug: bool = config_value("DEBUG", use_env=True, default=False)
    workers: int = config_value("WORKERS", rtype=int, default=4)
    max_connections: int = config_value("MAX_CONNECTIONS", rtype=int, default=100)

    def __post_init__(self):
        """Validate settings after initialization."""
        if self.workers < 1:
            raise ValueError("Workers must be at least 1")

        if self.workers > self.max_connections:
            raise ValueError(
                f"Workers ({self.workers}) cannot exceed "
                f"max_connections ({self.max_connections})"
            )

        if self.debug and self.workers > 1:
            import warnings
            warnings.warn(
                "Running with debug=True and multiple workers. "
                "Consider using workers=1 for debugging."
            )

# This will raise ValueError if validation fails
settings = Settings()
```

### Optional Settings with None Defaults

Handle optional configuration gracefully:

```python
from typing import Optional

@settings_class(filename="config.yml")
class Settings:
    # Optional email configuration
    smtp_host: Optional[str] = config_value(
        "SMTP_HOST",
        sections=["email"],
        default=None
    )

    smtp_port: Optional[int] = config_value(
        "SMTP_PORT",
        sections=["email"],
        rtype=int,
        default=None
    )

    @property
    def email_enabled(self) -> bool:
        return self.smtp_host is not None

    def send_email(self, to: str, subject: str, body: str):
        if not self.email_enabled:
            raise RuntimeError("Email not configured")
        # Send email logic...

settings = Settings()
if settings.email_enabled:
    settings.send_email("user@example.com", "Hello", "World")
```

---

## Comparison: Settings Classes vs get_setting

| Feature | Settings Classes | get_setting |
|---------|------------------|-------------|
| Type Safety | ✅ Full IDE support | ⚠️ Manual typing |
| Organization | ✅ Grouped in classes | ❌ Flat function calls |
| Reusability | ✅ Instantiate multiple times | ✅ Call anywhere |
| Validation | ✅ Via `__post_init__` | ❌ Manual validation |
| Composition | ✅ Nest classes easily | ❌ No structure |
| Immutability | ✅ Frozen dataclass | N/A |
| Best For | Application-wide config | Quick one-off settings |

## Best Practices

1. **Use Type Annotations**: Always annotate your settings attributes for better IDE support
2. **Provide Defaults**: Set sensible defaults to avoid runtime errors
3. **Group Related Settings**: Use separate classes for different configuration domains
4. **Validate Early**: Use `__post_init__` to catch configuration errors at startup
5. **Document Complex Settings**: Add docstrings to explain non-obvious configuration options
6. **Use Environment Variables for Secrets**: Never hardcode sensitive values; always use `use_env`

## Common Pitfalls

### Forgetting to Instantiate

```python
# Wrong: This is the class, not an instance
settings = AppSettings  # Missing ()

# Correct: Instantiate to resolve values
settings = AppSettings()
```

### Using Mutable Defaults

```python
# Avoid mutable defaults in config_value
bad: list[str] = config_value("LIST", default=[])  # Don't do this

# Use immutable defaults or factory patterns
good: tuple[str, ...] = config_value("LIST", default=())
```

### Circular Dependencies

```python
# Don't reference other settings during class definition
class Settings:
    # This won't work - other settings aren't resolved yet
    derived: str = some_function(Settings.other)  # Error!

    # Instead, use properties or __post_init__
    @property
    def derived(self) -> str:
        return some_function(self.other)
```

## Next Steps

- Review [ConfigParser and get_setting](parsers.md) for lower-level configuration access
- Check the [Usage Overview](index.md) for configuration hierarchy details
- Explore real-world examples in the [cookbook.yaml](../../cookbook.yaml) file
