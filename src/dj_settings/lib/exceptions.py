class SectionError(KeyError):
    def __init__(self, path: list[str]) -> None:
        msg = f"Section `{path[-1]}` not found"
        super().__init__(msg)
        self.__notes__ = [f"Sections searched: {' -> '.join(path)}"]
