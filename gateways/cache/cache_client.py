import json
from typing import List, Union

from common import config
from redis import StrictRedis


class CacheClient:

    def __init__(self) -> None:
        client_args = {
            'host': config.redis_host,
            'port': config.redis_port,
            'db': config.redis_db
        }

        client_args = {k:v for k,v in client_args.items() if v is not None}

        self.client = StrictRedis(**client_args) # type: ignore

    def set(self, collection: str, key: str, value: dict) -> bool:
        return self.client.set(self._get_context_key(collection, key), json.dumps(value))

    def get(self, collection: str, key: str) -> Union[dict, None]:
        value = self.client.get(self._get_context_key(collection, key))
        if value is not None:
            return json.loads(value.decode())
        
        return None

    def keys(self, collection: str) -> List[str]:
        return [self._extract_key_from_context(key.decode()) for key in self.client.keys() if key.decode().startswith(self._get_context_collection(collection))]

    def _extract_key_from_context(self, key: str) -> str:
        parts = key.split('.')
        return parts[-1]

    def _get_context_collection(self, collection: str) -> str:
        return f"{config.redis_key_prefix}.{collection}"

    def _get_context_key(self, collection: str, key: str) -> str:
        return f"{self._get_context_collection(collection)}.{key}"
