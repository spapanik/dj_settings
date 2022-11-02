import sys

MINOR = sys.version_info.minor

if MINOR >= 11:
    import tomllib

    toml_parser = tomllib.load
else:
    import tomli

    toml_parser = tomli.load
