from typing import Union

from common.configuration import HATHOR_NODES
from domain.network.node import Node
from gateways.node_gateway import NodeGateway
from gateways.clients.hathor_core_client import HathorCoreAsyncClient


class CollectNodesStatuses:

    def __init__(self, lambda_gateway: Union[NodeGateway, None] = None) -> None:
        self.lambda_gateway = lambda_gateway or NodeGateway()

    async def collect(self) -> None:
        for node in HATHOR_NODES:
            client = HathorCoreAsyncClient(node)
            node_gateway = NodeGateway(hathor_core_async_client=client)
            await node_gateway.get_node_status_async(self._send)

    def _send(self, data: dict) -> None:
        network = Node.from_status_dict(data)
        self.lambda_gateway.send_node_to_data_aggregator(network)
