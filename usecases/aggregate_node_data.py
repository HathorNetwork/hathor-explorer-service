from typing import Union

from deepdiff import DeepDiff
from gateways.node_gateway import NodeGateway


class AggregateNodeData:

    def __init__(self, node_gateway: Union[NodeGateway, None] = None) -> None:
        self.node_gateway = node_gateway or NodeGateway()

    def aggregate(self) -> Union[bool, None]:
        new_network = self.node_gateway.aggregate_network()
        old_network = self.node_gateway.get_network()

        networks_diff = DeepDiff(new_network, old_network)

        if networks_diff:
            return self.node_gateway.save_network(new_network)

        return True
