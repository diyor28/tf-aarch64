class Collection:
    path: str
    collection: str

    def __init__(self, path: str, collection: str):
        self.path = path
        self.collection = collection

    def _read(self):
        return

    def read_all(self) -> list[dict]:
        
        pass

    def insert(self, data: dict):
        pass

    def patch(self, pk: int, data: dict):
        pass

    def delete(self, pk: int):
        pass


class Store:
    _path: str
    builds: Collection

    def __init__(self, path: str):
        self._path = path
        self.builds = Collection(path, 'builds')
