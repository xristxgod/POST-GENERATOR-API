from typing import Any


class CRUD:
    @staticmethod
    def create(data: object) -> bool:
        raise NotImplementedError

    @staticmethod
    def read(**kwargs: Any) -> object:
        raise NotImplementedError
