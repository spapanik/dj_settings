# Settings Classes

Settings classes provide a type-safe, object-oriented approach to configuration
management. By using the `@settings_class` decorator and `config_value` helper, you can
define configuration schemas with full IDE support, type checking, and automatic value
resolution.

## Overview

Settings classes combine the power of Python dataclasses with dj_settings' configuration
resolution, giving you:

- **Type Safety**: Full type annotations with IDE autocomplete and static analysis support
- **Immutability**: Frozen dataclasses prevent accidental modification
- **One document**: N fields cost one document, shared by every field
- **Resolution at instantiation**: values are fetched when the class is instantiated, not
  when the module is imported

## Basic Usage

```python
from dj_settings import config_value, settings_class


@settings_class("/myapp/config.yml")
class AppSettings:
    # Simple setting with default
    debug: bool = config_value("DEBUG", default=False)

    # Setting from nested config section
    database_url: str = config_value(
        "url",
        sections=["database", "connection"],
        default="sqlite:///db.sqlite3",
    )

    # Setting with an explicit env var name
    secret_key: str = config_value(
        "SECRET_KEY", use_env="APP_SECRET_KEY", default="change-me-in-production"
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

The `@settings_class` decorator transforms a regular class into a frozen dataclass whose
fields resolve their configuration values during initialization.

### Signature

```python
settings_class(
    *paths: str | Path,
    force_type: SupportedType | None = None,
    dir_namespace: str = "",
    merge_arrays: bool = False,
) -> Callable[[type], type]
```

The parameters are exactly those of [`ConfigParser`](parsers.md#constructor-parameters):
the decorator builds one parser, and every `config_value` field shares its document.

### How It Works

1. The decorator builds a `ConfigParser` from its arguments
2. Every attribute assigned via `config_value()` becomes a dataclass field whose
   `default_factory` resolves the value through that parser
3. The class is converted to a frozen dataclass

Because resolution happens at instantiation:

- A missing required setting raises when the class is **instantiated**, rather than
  part-way through importing the module
- Environment changes between instantiations are visible, so tests can monkeypatch
  without reimporting
- A field can still be overridden by passing it to the constructor - which is also how a
  parsed CLI argument reaches the decorator path: `Settings(**overrides)`

### Example Config File Lookup

For a settings class defined as:

```python
@settings_class("/myapp/app.yml")
class Settings:
    value: str = config_value("setting")
```

The `value` attribute will be searched in this order:

1. Environment variable `SETTING` (derived; `use_env=True` is the default)
2. `/myapp/app.yml` → `setting`
3. `~/.config/app.yml` → `setting`
4. `/etc/app.yml` → `setting`
5. Default value (if provided)

Each `.yml` file can be overridden by its corresponding `.yml.d/` directory.

---

## The config_value Helper

The `config_value()` function records how one field is resolved. It is `get_setting`
minus `self`: the field records everything the parser does not already own.

### Signature

```python
config_value(
    name: str,                                           # Required: setting name
    *,
    cli_value: T | Sentinel = UNDEFINED,                 # Parsed CLI argument, if any
    use_env: bool | str = True,                          # Environment variable handling
    sections: Iterable[str] = (),                        # Config sections to traverse
    env_namespace: str | Sentinel = UNDEFINED,           # Derived-name prefix
    rtype: Callable[[object], T] | type | Sentinel = UNDEFINED,  # Coercion (optional)
    default: T | Sentinel = UNDEFINED,                   # Default value
    validator: Callable[[object], None] | None = None,   # Contract check (optional)
) -> Any
```

All parameters behave exactly as in
[`get_setting`](parsers.md#the-get_setting-method). Note that `merge_arrays` is **not** a
`config_value` parameter: it belongs to the document, so it is passed to
`@settings_class` instead.

#### `name` (Required)

The key name to search for in configuration files, and the final component of the
derived environment variable name.

#### `use_env`

```python
# Derive the variable name (sections + key, uppercased, joined with __)
debug: bool = config_value("debug")

# Read a custom variable, verbatim
api_key: str = config_value("API_KEY", use_env="MY_API_KEY")

# Prefix a custom variable; reads DJANGO__USER
username: str = config_value("username", use_env="USER", env_namespace="DJANGO")

# Disable env var checking
internal_flag: bool = config_value("FLAG", use_env=False)
```

#### `sections`

Navigate through nested configuration structures. Sections also participate in the
derived environment variable name.

```python
# For YAML like:
# database:
#   primary:
#     host: localhost

host: str = config_value("host", sections=["database", "primary"])
# environment: DATABASE__PRIMARY__HOST
```

#### `env_namespace`

Prefix the derived variable name, to keep every setting of an application under one
namespace:

```python
theme: str = config_value("theme", env_namespace="NEON_SSG", default="dark")
# environment: NEON_SSG__THEME

username: str = config_value(
    "username", sections=["database"], use_env="USER", env_namespace="DJANGO"
)
# environment: DJANGO__USER (sections and name do not participate)
```

#### `rtype`

Coerce values to specific types. If omitted, no conversion is performed and the value
keeps the type it had in the config file - so a YAML list stays a list, and `port: 8000`
stays an `int`. Environment variables are always strings, so an `rtype` is what turns
them into anything else.

Because nothing coerces the value to match your annotation, an `rtype` is worth setting
whenever the setting can come from the environment:

```python
# Integer conversion
port: int = config_value("PORT", rtype=int, default=8000)

# Boolean conversion
debug: bool = config_value(
    "DEBUG", rtype=lambda x: str(x).lower() in ("true", "1", "yes"), default=False
)
```

#### `default`

Fallback value if the setting is not found. Returned as-is: never coerced, never
validated.

```python
# With default
cache_ttl: int = config_value("CACHE_TTL", rtype=int, default=300)

# Without default (raises SettingNotFoundError at instantiation if missing)
required_secret: str = config_value("REQUIRED_SECRET")
```

#### `validator`

A callable that receives the coerced value and only raises:

```python
def positive(value: object) -> None:
    if not isinstance(value, int) or value <= 0:
        msg = f"{value} is not a positive integer"
        raise ValueError(msg)


workers: int = config_value("workers", rtype=int, default=4, validator=positive)
```

---

## Advanced Patterns

### Multiple Configuration Files

Use different stems for different settings groups:

```python
from dj_settings import config_value, settings_class


# Database settings from db.yml
@settings_class("/myapp/db.yml")
class DatabaseSettings:
    url: str = config_value("url", sections=["connection"])
    pool_size: int = config_value("pool_size", rtype=int, default=5)


# App settings from app.yml
@settings_class("/myapp/app.yml")
class AppSettings:
    debug: bool = config_value("debug", default=False)
    secret_key: str = config_value("secret_key")


# Compose them
class Settings:
    db = DatabaseSettings()
    app = AppSettings()
```

### Overriding Fields at Instantiation

Every `config_value` field is an ordinary dataclass field, so a caller can override it -
this is how parsed CLI arguments reach a settings class:

```python
overrides = {}
if args.port is not None:
    overrides["port"] = args.port

settings = AppSettings(**overrides)
```

### Environment-Specific Settings

```python
@settings_class("config.yml")
class Settings:
    environment: str = config_value(
        "environment", use_env="APP_ENV", default="development"
    )

    debug: bool = config_value(
        "debug",
        rtype=lambda x: str(x).lower() == "true",
        default=False,  # Production-safe default
    )

    database_url: str = config_value(
        "url",
        sections=["database"],
        default="sqlite:///dev.db",
    )


settings = Settings()

# In production: export APP_ENV=production DATABASE__URL=postgres://...
# In development: use config file defaults
```

### Validation and Post-Processing

Per-field contracts belong in `validator`; cross-field validation belongs in
`__post_init__`:

```python
from dj_settings import config_value, settings_class


@settings_class("config.yml")
class Settings:
    workers: int = config_value("workers", rtype=int, default=4)
    max_connections: int = config_value("max_connections", rtype=int, default=100)

    def __post_init__(self):
        if self.workers > self.max_connections:
            raise ValueError(
                f"Workers ({self.workers}) cannot exceed "
                f"max_connections ({self.max_connections})"
            )
```

### Optional Settings with None Defaults

A default is never coerced, which is what allows `None` as a default for an
otherwise-typed setting:

```python
@settings_class("config.yml")
class Settings:
    smtp_host: str | None = config_value("host", sections=["email"], default=None)
    smtp_port: int | None = config_value(
        "port", sections=["email"], rtype=int, default=None
    )

    @property
    def email_enabled(self) -> bool:
        return self.smtp_host is not None
```

---

## Best Practices

1. **Use Type Annotations**: Always annotate your settings attributes for better IDE support
2. **Provide Defaults**: Ship a complete default configuration - it is also what makes
   every setting environment-overridable
3. **Group Related Settings**: Use separate classes for different configuration domains
4. **Instantiate at startup**: A missing required setting raises at instantiation, so
   instantiate early to catch configuration errors at startup
5. **Use Environment Variables for Secrets**: Never hardcode sensitive values

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
