import json
import abc
from typing import Any, Optional


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()

    def save_state(self, state: dict) -> None:
        data = self.retrieve_state()
        data.update(state)
        with open(self.file_path, 'w') as file:
            json.dump(data, file)


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        data = self.storage.retrieve_state()
        data[key] = value
        self.storage.save_state(data)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        data = self.storage.retrieve_state()
        return data.get(key, None)
