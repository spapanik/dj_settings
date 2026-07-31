from __future__ import annotations


class SettingNotFoundError(LookupError):
    def __init__(self, path: list[str], layers: list[str]) -> None:
        msg = f"No value found for setting `{'.'.join(path)}`"
        super().__init__(msg)
        self.__notes__ = [f"Layers consulted: {'; '.join(layers)}"]
