from typing import Union

from common.configuration import HATHOR_NODES
from domain.network.node import Node
from gateways.clients.hathor_core_client import HathorCoreAsyncClient
from gateways.node_gateway import NodeGateway


class CollectNodesStatuses:
    """ Usecase class to collect nodes statuses
    """
    def __init__(self, node_gateway: Union[NodeGateway, None] = None) -> None:
        self.node_gateway = node_gateway or NodeGateway()

    async def collect(self) -> None:
        """Collect nodes statuses and send them to data aggregator
        """
        for node in HATHOR_NODES:
            client = HathorCoreAsyncClient(node)
            node_gateway = NodeGateway(hathor_core_async_client=client)
            await node_gateway.get_node_status_async(self._send)

    def _send(self, data: dict) -> None:
        node = Node.from_status_dict(data)
        self.node_gateway.send_node_to_data_aggregator(node)
