

class LinkedFile:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def _has_changed(self) -> bool:
        pass

    def update(self) -> None:
        pass

    def write_metadata(self) -> None:
        pass

    def write_latex(self) -> None:
        pass

    def remove(self) -> None:
        pass
