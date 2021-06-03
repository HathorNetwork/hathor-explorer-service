from typing import Union

from domain.network.node import Node
from gateways.cache.cache_gateway import CacheGateway


class SaveNodeData:

    def __init__(self, cache_gateway: Union[CacheGateway, None] = None) -> None:
        self.cache_gateway = cache_gateway or CacheGateway()

    def save(self, payload: dict) -> Union[bool, None]:
        node = Node.from_dict(payload)
        return self.cache_gateway.save_node(node.id, node)
