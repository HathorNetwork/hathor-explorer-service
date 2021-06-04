from typing import Union

from gateways.node_gateway import NodeGateway


class GetNode:

    def __init__(self, node_gateway: Union[NodeGateway, None] = None) -> None:
        self.node_gateway = node_gateway or NodeGateway()

    def get(self, id: str) -> Union[dict, None]:
        node = self.node_gateway.get_node(id)

        if node is not None:
            return node.to_dict()

        return None
