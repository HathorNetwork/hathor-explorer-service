from typing import Union

from gateways.cache.cache_gateway import CacheGateway


class GetNode:

    def __init__(self, cache_gateway: Union[CacheGateway, None] = None) -> None:
        self.cache_gateway = cache_gateway or CacheGateway()

    def get(self, id: str) -> Union[dict, None]:
        network = self.cache_gateway.get_node(id)

        if network is not None:
            return network.to_dict()

        return None
