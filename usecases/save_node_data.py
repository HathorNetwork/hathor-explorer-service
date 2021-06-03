from typing import Union

from domain.network.node import Node
from gateways.node_gateway import NodeGateway


class SaveNodeData:

    def __init__(self, cache_gateway: Union[NodeGateway, None] = None) -> None:
        self.cache_gateway = cache_gateway or NodeGateway()

    def save(self, payload: dict) -> Union[bool, None]:
        node = Node.from_dict(payload)
        return self.cache_gateway.save_node(node.id, node)
