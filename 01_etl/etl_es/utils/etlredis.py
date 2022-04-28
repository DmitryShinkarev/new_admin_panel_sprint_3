import abc
from datetime import datetime

from redis import Redis


class BaseStorage:

    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class RedisStorage(BaseStorage):

    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def get_status(self, app: str):
        key = "status:" + app
        return self.redis_adapter.get(key)

    def set_modified_time(self, index: str, lasttime: datetime) -> datetime:
        key = index + ":modified"
        self.redis_adapter.set(key, lasttime.isoformat())
        time = self.redis_adapter.get(key)
        return datetime.fromisoformat(time)

    def get_modified_time(self, index: str) -> datetime:
        key = index + ":modified"
        time = self.redis_adapter.get(key)
        return time

    def set_status(self, app: str, status: str):
        key = "status:" + app
        self.redis_adapter.set(key, status)
        return self.redis_adapter.get(key)

    def push_modified_filmid(self, id: str):
        self.redis_adapter.lrem("modified_id", 0, id)
        self.redis_adapter.lpush("modified_id", id)

    def get_modified_filmid(self) -> list:
        len = self.redis_adapter.llen("modified_id")
        moviesid = self.redis_adapter.lrange("modified_id", 0, len)
        return moviesid

    def del_modified_filmid(self, id: str):
        self.redis_adapter.lrem("modified_id", 0, id)
