# Configuration Parsers

`ConfigParser` owns both halves of the pipeline: it _is_ the merged document, and its
`get_setting` method is one resolution over it. This guide covers both.

## ConfigParser Class

The `ConfigParser` class merges the file tiers of every stem it is given into one
document, automatically handling `.d` directory overrides.

### Basic Usage

```python
from dj_settings import ConfigParser

parser = ConfigParser("/myapp/config.yml")

# Access the merged configuration data
config_data = parser.data
print(config_data["database"]["host"])

# Resolve one value through the full hierarchy
host = parser.get_setting("host", sections=["database"], default="localhost")
```

### How It Works

Every path is a **stem**. For each stem, `ConfigParser` reads three tiers, later ones
winning:

1. System: `/etc/<basename>`, plus `/etc/<basename>.d/*`
2. User: `$XDG_CONFIG_HOME/<basename>` (defaults to `~/.config`), plus its `.d/*`
3. Project: the stem exactly as given, plus its `.d/*`

Missing files are simply skipped. With more than one stem, merging is stem-major: the
first stem's tiers in full, then the second stem's, and so on, later winning.

Example file processing order for `ConfigParser("/myapp/config.yml")`:

```
/etc/config.yml                    # System tier
/etc/config.yml.d/01-defaults.yml  # System overrides
~/.config/config.yml               # User tier
~/.config/config.yml.d/custom.yml  # User overrides
/myapp/config.yml                  # Project tier (wins)
```

The document is built once per parser, lazily, on first access, and every `get_setting`
call on that parser reuses it. A caller who needs to pick up changed files constructs a
new parser.

### Constructor Parameters

```python
ConfigParser(
    *paths: str | Path,                       # Stems, each expanding into its tier set
    force_type: SupportedType | None = None,  # Optional: force file type
    dir_namespace: str = "",                  # Optional: user/system tier subdirectory
    merge_arrays: bool = False,               # Optional: merge lists instead of replacing
)
```

| Parameter       | Type                    | Default | Description                                                                   |
| --------------- | ----------------------- | ------- | ----------------------------------------------------------------------------- |
| `*paths`        | `str \| Path`           | `()`    | Configuration stems; each expands into project, user, and system tiers        |
| `force_type`    | `SupportedType \| None` | `None`  | Force a specific parser type (`"yaml"`, `"toml"`, `"json"`, `"ini"`, `"env"`) |
| `dir_namespace` | `str`                   | `""`    | Resolve the user and system tiers under `<tier>/<dir_namespace>/<basename>`   |
| `merge_arrays`  | `bool`                  | `False` | If `True`, concatenate arrays instead of replacing them                       |

These parameters select or combine files, so they belong to the document: all of them are
constructor-only, which is what makes the document shareable across every key a caller
reads.

With `dir_namespace` set, the flat file at the user and system tiers is **not** also
consulted; extension still happens through the ordinary `.d` mechanism
(`<tier>/<dir_namespace>/<basename>.d/*`). The project location is given by the stem
itself, so `dir_namespace` does not affect it.

### The `data` Property

Returns the merged file layers as a dictionary - and nothing else: the environment is
never merged into it. Reading a merged configuration without asking for one specific
value is a legitimate use on its own.

```python
parser = ConfigParser("config.yml")
config = parser.data  # Triggers parsing on first access
print(config["app"]["name"])
```

## The `get_setting` Method

`ConfigParser.get_setting` is the only value accessor. It resolves one key through the
full hierarchy: CLI value, environment variable, the document, then the default.

### Basic Usage

```python
from dj_settings import ConfigParser

parser = ConfigParser("/myapp/config.yml")

# Simple usage with default
debug = parser.get_setting("debug", default=False)

# Full usage
database_url = parser.get_setting(
    "url",
    use_env=True,
    sections=["database"],
    env_namespace="MYAPP",  # reads MYAPP__DATABASE__URL
    rtype=str,
    default="sqlite:///db.sqlite3",
)
```

### Function Signature

```python
get_setting(
    name: str,                                           # Required: setting name
    *,
    cli_value: T | Sentinel = UNDEFINED,                 # Parsed CLI argument, if any
    use_env: bool | str = True,                          # Environment variable handling
    sections: Iterable[str] = (),                        # Config sections to traverse
    env_namespace: str | Sentinel = UNDEFINED,           # Derived-name prefix
    rtype: Callable[[object], T] | type | Sentinel = UNDEFINED,  # Coercion (optional)
    default: T | Sentinel = UNDEFINED,                   # Default value
    validator: Callable[[object], None] | None = None,   # Contract check (optional)
) -> T
```

### Parameters

#### `name` (Required)

The key to resolve. It is looked up in the configuration files under `sections`, and it
is the final component of the derived environment variable name.

#### `cli_value`

A value obtained from a parsed CLI argument. When given, it outranks every other layer.
Pass `UNDEFINED` (the default) to mean "no CLI value was supplied".

```python
from dj_settings import UNDEFINED

parser.get_setting(
    "port",
    cli_value=args.port if args.port is not None else UNDEFINED,
    rtype=int,
    default=8000,
)
```

#### `use_env`

Controls environment variable checking:

| Value   | Behavior                                                         |
| ------- | ---------------------------------------------------------------- |
| `True`  | Derive the name from `env_namespace`, `sections`, and `name`     |
| `str`   | Use an explicit basename, optionally prefixed by `env_namespace` |
| `False` | Skip the environment: file-only lookup                           |

`use_env=False` with no `default` _is_ file-only lookup - a first-class mode, not a
convenience flag.

#### `sections`

The section path to the key, in configuration files _and_ in the derived variable name.

```python
# For config structure:
# database:
#   connection:
#     url: postgres://...

parser.get_setting("url", sections=["database", "connection"])
# files: database -> connection -> url
# environment: DATABASE__CONNECTION__URL
```

#### `env_namespace`

A prefix for the environment variable name. Passing it implies that the environment is
enabled, so combining it with `use_env=False` raises `ValueError`.

`env_namespace=""` is meaningful and distinct from not passing it. With `use_env=True`,
it drops the namespace while keeping the sections and key; with a string `use_env`, it
leaves that explicit basename unchanged.

```python
parser.get_setting("user", sections=["application"], env_namespace="DJANGO")
# reads DJANGO__APPLICATION__USER

parser.get_setting(
    "username", sections=["database"], use_env="USER", env_namespace="DJANGO"
)
# reads DJANGO__USER; sections and name do not participate with explicit use_env
```

With a string `use_env`, the explicit basename remains verbatim while the namespace is
uppercased: `use_env="app_user", env_namespace="django"` reads
`DJANGO__app_user`. Without a namespace, `"foo"` still reads `foo`, not `FOO`.

Derivation is one-way: a variable name is never parsed back into sections or keys, and
the environment cannot bring a new key into existence - it can only supply the value for
a key you name.

#### `rtype`

A callable to coerce the resolved value. If omitted, **no conversion is performed** and
the value is returned as parsed.

This matters because configuration formats are typed: a list in YAML/TOML/JSON stays a
list, and `port: 8000` stays an `int`. Environment variables are always strings, so they
are returned as strings unless you pass an `rtype`.

`rtype` is indifferent to which layer produced the value: with `rtype=float`, the string
`"2.3"` from the environment returns `2.3`, and the int `1` from a YAML file returns
`1.0`. We parse what you ask for; we do not repair it: `rtype=bool` on the string
`"false"` returns `True`, because `bool("false")` is `True` - pass a proper parser if you
need one.

`rtype` is **not** applied to `default`; a default is returned exactly as you passed it,
so pass it pre-typed. This is deliberate: it allows `None` (or any sentinel of yours) as
a default for an otherwise-typed setting.

```python
# Convert to integer
port = parser.get_setting("PORT", rtype=int, default=8000)

# Convert to boolean, correctly
debug = parser.get_setting(
    "DEBUG", rtype=lambda x: str(x).lower() == "true", default=False
)

# Custom type conversion
from datetime import datetime

created = parser.get_setting("CREATED", rtype=datetime.fromisoformat)
```

#### `default`

The fallback value if no layer produced a value. Returned as-is: never coerced, never
validated. If not provided and the setting is missing, `SettingNotFoundError` is raised.

#### `validator`

A callable that receives the coerced value and only raises; it never returns a value and
never coerces one. Coercion is `rtype`'s job. The default is `None`, meaning no
validation. The validator is not applied to a returned `default` - the default is your
own literal.

```python
def port_range(value: object) -> None:
    if not isinstance(value, int) or not 1 <= value <= 65535:
        msg = f"{value} is not a valid port"
        raise ValueError(msg)


port = parser.get_setting("port", sections=["server"], rtype=int, validator=port_range)
```

### Return Value and Exceptions

**Returns:** The resolved value, coerced by `rtype` for layers other than the default

**Raises:**

- `SettingNotFoundError`: if no layer supplied a value and no default was given. The
  exception reports the section path being resolved and which layers were consulted
- `ValueError`: if `env_namespace` is combined with `use_env=False`
- Whatever your `validator` raises

### Error Handling

```python
from dj_settings import ConfigParser
from dj_settings.lib.exceptions import SettingNotFoundError

parser = ConfigParser("config.yml")

# With a default: missing sections are silently handled
value = parser.get_setting("setting", sections=["nonexistent"], default=None)

# Without a default: missing setting raises
try:
    value = parser.get_setting("setting", sections=["nonexistent"])
except SettingNotFoundError as e:
    print(f"Required setting not found: {e}")
```

---

## Comparison: `data` vs `get_setting`

| Feature               | `data`                   | `get_setting`                                       |
| --------------------- | ------------------------ | --------------------------------------------------- |
| Use Case              | Read the merged document | Resolve individual settings                         |
| Fallback Chain        | Files only               | Yes (CLI → env → project → user → system → default) |
| Environment Variables | Never                    | Yes (optional)                                      |
| Type Conversion       | Manual                   | Built-in (`rtype`)                                  |
| Validation            | Manual                   | Built-in (`validator`)                              |
| Best For              | Whole-config inspection  | Getting specific settings                           |

## Next Steps

- Learn about [Settings Classes](decorator.md) for type-safe configuration objects
- Review the [Usage Overview](index.md) for configuration hierarchy details
