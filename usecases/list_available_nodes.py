from typing import List

from gateways.cache.cache_gateway import CacheGateway


class ListAvailableNodes:

    def __init__(self, cache_gateway: CacheGateway = None) -> None:
        self.cache_gateway = cache_gateway or CacheGateway()
    
    def list(self) -> List[str]:
        return self.cache_gateway.list_network_keys()
