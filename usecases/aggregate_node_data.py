from typing import Union

from deepdiff import DeepDiff

from gateways.node_gateway import NodeGateway


class AggregateNodeData:

    def __init__(self, node_gateway: Union[NodeGateway, None] = None) -> None:
        self.node_gateway = node_gateway or NodeGateway()

    def aggregate(self) -> Union[bool, None]:
        new_network = self.node_gateway.aggregate_network()
        old_network = self.node_gateway.get_network()

        if old_network:
            regex_path_to_exclude = r"root\['(nodes|peers)'\]\[\d+\]\['uptime'\]"
            new_dict = new_network.to_dict()
            old_dict = old_network.to_dict()
            networks_diff = DeepDiff(new_dict, old_dict, ignore_order=True, exclude_regex_paths=regex_path_to_exclude)

        if (not old_network) or networks_diff:
            return self.node_gateway.save_network(new_network)

        return True
