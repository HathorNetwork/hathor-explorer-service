import json
from typing import List, Union

from redis import StrictRedis

from common.configuration import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_KEY_PREFIX


class CacheClient:
    """This is an abstraction and convenience for redis
    """
    def __init__(self) -> None:
        client_args = {
            'host': REDIS_HOST,
            'port': REDIS_PORT,
            'db': REDIS_DB
        }

        client_args = {k: v for k, v in client_args.items() if v is not None}

        self.client = StrictRedis(**client_args)  # type: ignore

    def set(self, collection: str, key: str, value: dict) -> Union[bool, None]:
        """Saves a dict into cache

        :param collection: a name to separate contexts
        :type collection: str
        :param key: an identifier for the entry
        :type key: str
        :param value: the dict to be saved
        :type value: dict
        :return: if it saved successfuly or not
        :rtype: bool
        """
        return self.client.set(self._get_context_key(collection, key), json.dumps(value))

    def get(self, collection: str, key: str) -> Union[dict, None]:
        """Retrieves a dict from cache

        :param collection: a name to separate contexts
        :type collection: str
        :param key: an identifier for the entry
        :type key: str
        :return: the retrived data or None if nothing found
        :rtype: Union[dict, None]
        """
        value = self.client.get(self._get_context_key(collection, key))
        if value is not None:
            return json.loads(value.decode())

        return None

    def keys(self, collection: str) -> List[str]:
        """Retrieves all keys from a given context

        :param collection: a name to separate contexts
        :type collection: str
        :return: the list of keys
        :rtype: List[str]
        """
        return [self._extract_key_from_context(key.decode()) for key in self.client.keys()
                if key.decode().startswith(self._get_context_collection(collection))]

    def _extract_key_from_context(self, key: str) -> str:
        """Returns the simple key from a raw key. This is the reverse operation of `_get_context_key`

        :param key: raw key retrived from cache
        :type key: str
        :return: simple version of key, as it is required on `get` and `set` methods
        :rtype: str
        """
        parts = key.split('.')
        return parts[-1]

    def _get_context_collection(self, collection: str) -> str:
        """Returns a collection with greater (project) context

        :param collection: a name to separete contexts
        :type collection: str
        :return: configured project prefix + given collection
        :rtype: str
        """
        return f"{REDIS_KEY_PREFIX}.{collection}"

    def _get_context_key(self, collection: str, key: str) -> str:
        """Returns the complete key ready to be saved in cache

        :param collection: a name to separete contexts
        :type collection: str
        :param key: an identifier for the entry
        :type key: str
        :return: prefix + collection + key
        :rtype: str
        """
        return f"{self._get_context_collection(collection)}.{key}"
