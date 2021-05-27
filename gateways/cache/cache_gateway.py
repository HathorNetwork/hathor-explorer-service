from typing import List, Union

from domain.network.network import Network
from gateways.cache.cache_client import CacheClient


class CacheGateway:

    def __init__(self, client: Union[CacheClient, None] = None) -> None:
        self.client = client or CacheClient()

    def save_network(self, id: str, network: Network) -> bool:
        return self.client.set('network', id, network.to_dict())

    def get_network(self, id: str) -> Union[Network, None]:
        value = self.client.get('network', id)

        if value is not None:
            return Network.from_dict(value)

        return None

    def list_network_keys(self) -> List[str]:
        return self.client.keys('network')
