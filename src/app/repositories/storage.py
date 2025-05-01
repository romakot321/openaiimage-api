from pathlib import Path
import os


class StorageRepository:
    base_directory = Path("storage")

    def __init__(self):
        if not self.base_directory.exists():
            os.mkdir(self.base_directory)

    def store_file(self, filename: str, file_body: bytes):
        with open(self.base_directory / filename, "wb") as f:
            f.write(file_body)

    def get_file(self, filename: str) -> bytes | None:
        if not (self.base_directory / filename).exists():
            return None
        with open(self.base_directory / filename, "rb") as f:
            return f.read()
