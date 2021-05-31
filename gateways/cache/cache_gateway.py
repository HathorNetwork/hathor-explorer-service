from typing import List, Union

from domain.network.network import Network
from gateways.cache.cache_client import CacheClient


class CacheGateway:
    """Gateway for cache manipulation

    :param cache_client: Client for cache, dafults to CacheClient
    :type cache_client: :py:class:`gateways.cache.cache_client.CacheClient`, optional
    """
    def __init__(self, cache_client: Union[CacheClient, None] = None) -> None:
        self.cache_client = cache_client or CacheClient()

    def save_network(self, id: str, network: Network) -> bool:
        """Saves Network data into cache with id as key

        :param id: identifier for the data
        :type id: str
        :param network: Network object with data
        :type network: :py:class:`domain.network.network.Network`
        :return: If saved successfuly or not
        :rtype: bool
        """
        return self.cache_client.set('network', id, network.to_dict())

    def get_network(self, id: str) -> Union[Network, None]:
        """Retrives network data for given id

        :param id: data identifier
        :type id: str
        :return: Network data or None if nothing found
        :rtype: Union[Network, None]
        """
        value = self.cache_client.get('network', id)

        if value is not None:
            return Network.from_dict(value)

        return None

    def list_network_keys(self) -> List[str]:
        """List current ids of saved networks

        :return: list of ids
        :rtype: List[str]
        """
        return self.cache_client.keys('network')
