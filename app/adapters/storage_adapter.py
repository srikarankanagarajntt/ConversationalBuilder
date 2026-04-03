from pathlib import Path

class StorageAdapter:
    def __init__(self) -> None:
        self.output_dir = Path("generated")
        self.output_dir.mkdir(exist_ok=True)

    def store_generated_file(self, file_name: str, content: bytes) -> str:
        path = self.output_dir / file_name
        path.write_bytes(content)
        return f"/generated/{file_name}"

_storage_adapter = StorageAdapter()

def get_storage_adapter() -> StorageAdapter:
    return _storage_adapter
