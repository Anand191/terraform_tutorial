from abc import ABC

import redis


class collection_cache(ABC):
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        super().__init__()
        self.redis_pool = redis.ConnectionPool.from_url(redis_url)
        self.redis_conn = redis.Redis(connection_pool=self.redis_pool)

    def flush(self, key):
        self.redis_conn.delete(key)

    def check(self, key):
        return self.redis_conn.exists(key) == 1

    def set(self, key, value):
        self.redis_conn.set(key, value)

    def get(self, key):
        return self.redis_conn.get(key).decode("utf-8")
