from typing import Union

from deepdiff import DeepDiff
from deepdiff.model import DiffLevel

from gateways.node_gateway import NodeGateway


class EarlyStopDiff:
    """ Stop the diff when we find an error

    From the docs example at:
    https://zepworks.com/deepdiff/5.7.0/custom.html#custom-operators
    """
    def match(self, level: DiffLevel) -> bool:
        return True

    def give_up_diffing(self, level: DiffLevel, diff_instance: DeepDiff) -> bool:
        return any(diff_instance.tree.values())


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
            networks_diff = DeepDiff(new_dict, old_dict, ignore_order=True, exclude_regex_paths=regex_path_to_exclude,
                                     custom_operators=[EarlyStopDiff()])

        if (not old_network) or networks_diff:
            return self.node_gateway.save_network(new_network)

        return True
