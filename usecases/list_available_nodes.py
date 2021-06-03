from typing import List, Union

from gateways.node_gateway import NodeGateway


class ListAvailableNodes:

    def __init__(self, cache_gateway: Union[NodeGateway, None] = None) -> None:
        self.cache_gateway = cache_gateway or NodeGateway()

    def list(self) -> List[str]:
        return self.cache_gateway.list_node_keys()
