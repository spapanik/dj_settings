# Usage Guide

## Configuration Hierarchy

`dj_settings` resolves every setting through one fixed lookup order. The first layer that
holds a value wins:

1. **CLI argument** - passed as `cli_value`
2. **Environment variable** - when `use_env` is enabled
3. **Project value** - the stem as given, including its implied `.d/` directories
4. **User value** - `$XDG_CONFIG_HOME` (defaults to `~/.config`), including its implied `.d/` directories
5. **System value** - `/etc`, including its implied `.d/` directories
6. **Default value** - provided as fallback

Each configuration file can be extended by files in its `.d` directory. For example, if
you have `/etc/config.yml`, any YAML files in `/etc/config.yml.d/` will be merged on top,
processed in alphabetical order.

Coercion happens only through `rtype`, and only on a value that some layer actually
produced. Layers 1-5 are coerced when `rtype` is given; the default is returned exactly
as you passed it and is never coerced.

### Stems

A path given to `ConfigParser` or `@settings_class` is a **stem**, not a file. Each stem
expands into its own tier set: the location as given (project), plus the user and system
tiers derived from its basename, each with its `.d` directory. An application cannot pass
a path that locks the person running it out of contributing `~/.config` or `/etc`
configuration - there is no opt-out.

```
Stem: /myapp/config.yml
                     ↓
System Config: /etc/config.yml (+ /etc/config.yml.d/)
                     ↓ (overridden by)
User Config: ~/.config/config.yml (+ ~/.config/config.yml.d/)
                     ↓ (overridden by)
Project Config: /myapp/config.yml (+ /myapp/config.yml.d/)
```

With more than one stem, merging is **stem-major**: the first stem's tiers are merged in
full, then the second stem's, and so on, later winning. Note the consequence: a later
stem's _system_ file outranks an earlier stem's _project_ file. The hierarchy above holds
within a stem; applications that need it to hold globally pass one stem.

### Environment Variable Names

When `use_env=True`, the variable name is derived from the namespace, the sections in
order, and the key - uppercased and joined with `__`:

```python
parser.get_setting("user", sections=["application"], env_namespace="DJANGO")
# reads DJANGO__APPLICATION__USER
```

Environment values are always strings; no type is ever inferred from them. `rtype` still
applies, exactly as it applies to a value from any other layer. Variables may override a
setting; they are never required - an unset variable simply falls through to the next
layer.

## Public API

`dj_settings` provides three entry points, which differ only in who owns the document:

| Component                                                       | Type      | Purpose                                            |
| --------------------------------------------------------------- | --------- | -------------------------------------------------- |
| [`ConfigParser`](parsers.md#configparser-class)                 | Class     | Parse and merge the file tiers into one document   |
| [`ConfigParser.get_setting`](parsers.md#the-get_setting-method) | Method    | Resolve one value through the full hierarchy       |
| [`settings_class`](decorator.md)                                | Decorator | Create type-safe settings classes                  |
| [`config_value`](decorator.md#the-config_value-helper)          | Helper    | Define configurable attributes in settings classes |

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
from dj_settings import ConfigParser

parser = ConfigParser("/myapp/config.yml")

# Get a setting with the full fallback chain
debug = parser.get_setting("debug", sections=["app"], default=False)
```

### Reading the Merged Document

```python
from dj_settings import ConfigParser

# Two stems, merged stem-major
parser = ConfigParser("/myapp/config.yml", "/myapp/extra.yml", merge_arrays=True)

# Access the merged file layers (no environment)
data = parser.data
```

### Type-Safe Settings Class

```python
from dj_settings import config_value, settings_class


@settings_class("/myapp/config.yml")
class AppSettings:
    debug: bool = config_value("DEBUG", default=False)
    database_url: str = config_value("url", sections=["database"])
    workers: int = config_value("workers", rtype=int, default=4)


settings = AppSettings()  # values resolve here, at instantiation
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

### Directory Namespaces

With `dir_namespace` set, the user and system tiers resolve
`<tier>/<dir_namespace>/<basename>` instead of `<tier>/<basename>`. The flat file at that
tier is **not** also consulted, so adding a `dir_namespace` is a breaking change for the
consumers of your configuration.

```python
parser = ConfigParser("/myapp/config.yml", dir_namespace="myapp")
# system tier: /etc/myapp/config.yml
# user tier:   ~/.config/myapp/config.yml
```

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
# Derive the variable name (sections + key, uppercased, joined with __)
parser.get_setting("debug", sections=["app"])  # Checks APP__DEBUG

# Prefix the derived name with a namespace: MYAPP__APP__DEBUG
parser.get_setting("debug", sections=["app"], env_namespace="MYAPP")

# Use an explicit variable name, verbatim
parser.get_setting("debug_mode", use_env="app_debug")  # Checks app_debug, not APP_DEBUG

# Prefix an explicit variable name; sections and setting name are ignored: DJANGO__USER
parser.get_setting(
    "username", sections=["database"], use_env="USER", env_namespace="DJANGO"
)

# Disable the environment: file-only lookup
parser.get_setting("setting", use_env=False)
```

## Next Steps

- Learn about [ConfigParser and get_setting](parsers.md) for detailed API reference
- Explore [Settings Classes](decorator.md) for type-safe configuration
- Check out real-world examples in the [cookbook.yaml](../../cookbook.yaml) file
