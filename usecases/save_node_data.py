from typing import Union

from domain.network.node import Node
from gateways.node_gateway import NodeGateway

from common.configuration import NODE_CACHE_TTL


class SaveNodeData:

    def __init__(self, node_gateway: Union[NodeGateway, None] = None) -> None:
        self.node_gateway = node_gateway or NodeGateway()

    def save(self, payload: dict) -> Union[bool, None]:
        node = Node.from_dict(payload)
        return self.node_gateway.save_node(node.id, node, NODE_CACHE_TTL)
