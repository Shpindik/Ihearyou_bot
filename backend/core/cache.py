import json
from typing import Any, Optional

import redis

from backend.core.config import settings


class Cache:
    def __init__(self):
        self._client: Optional[redis.Redis] = None

    def client(self) -> Optional[redis.Redis]:
        if self._client is not None:
            return self._client
        if not settings.redis_url:
            return None
        self._client = redis.from_url(settings.redis_url, decode_responses=True)
        return self._client

    def get_json(self, key: str) -> Optional[Any]:
        client = self.client()
        if not client:
            return None
        data = client.get(key)
        return json.loads(data) if data else None

    def set_json(self, key: str, value: Any, ttl_sec: int = 300) -> None:
        client = self.client()
        if not client:
            return
        client.set(key, json.dumps(value), ex=ttl_sec)

    def delete(self, key: str) -> None:
        client = self.client()
        if not client:
            return
        client.delete(key)

    def delete_prefix(self, prefix: str) -> None:
        client = self.client()
        if not client:
            return
        for key in client.scan_iter(f"{prefix}*"):
            client.delete(key)


cache = Cache()
