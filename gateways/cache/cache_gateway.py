from typing import List, Union

from domain.network.node import Node
from gateways.cache.cache_client import CacheClient


class CacheGateway:
    """Gateway for cache manipulation

    :param cache_client: Client for cache, dafults to CacheClient
    :type cache_client: :py:class:`gateways.cache.cache_client.CacheClient`, optional
    """
    def __init__(self, cache_client: Union[CacheClient, None] = None) -> None:
        self.cache_client = cache_client or CacheClient()

    def save_node(self, id: str, node: Node) -> Union[bool, None]:
        """Saves Node data into cache with id as key

        :param id: identifier for the data
        :type id: str
        :param node: Node object with data
        :type node: :py:class:`domain.network.node.Node`
        :return: If saved successfuly or not
        :rtype: bool
        """
        return self.cache_client.set('node', id, node.to_dict())

    def get_node(self, id: str) -> Union[Node, None]:
        """Retrives node data for given id

        :param id: data identifier
        :type id: str
        :return: Node data or None if nothing found
        :rtype: Union[Node, None]
        """
        value = self.cache_client.get('node', id)

        if value is not None:
            return Node.from_dict(value)

        return None

    def list_node_keys(self) -> List[str]:
        """List current ids of saved nodes

        :return: list of ids
        :rtype: List[str]
        """
        return self.cache_client.keys('node')
