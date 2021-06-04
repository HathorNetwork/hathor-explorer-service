from typing import List, Union

from gateways.node_gateway import NodeGateway


class ListAvailableNodes:

    def __init__(self, node_gateway: Union[NodeGateway, None] = None) -> None:
        self.node_gateway = node_gateway or NodeGateway()

    def list(self) -> List[str]:
        return self.node_gateway.list_node_keys()
