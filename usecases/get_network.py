from typing import Optional

from gateways.node_gateway import NodeGateway


class GetNetwork:
    def __init__(self, node_gateway: Optional[NodeGateway] = None) -> None:
        self.node_gateway = node_gateway or NodeGateway()

    def get(self) -> Optional[dict]:
        network = self.node_gateway.get_network()

        if network is not None:
            return network.to_dict()

        return None
