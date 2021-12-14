from typing import Optional

from common.configuration import HATHOR_NODES
from common.logging import get_logger
from domain.network.node import Node
from gateways.clients.hathor_core_client import HathorCoreAsyncClient
from gateways.node_gateway import NodeGateway

logger = get_logger()


class CollectNodesStatuses:
    """ Usecase class to collect nodes statuses
    """
    def __init__(self, node_gateway: Optional[NodeGateway] = None) -> None:
        self.node_gateway = node_gateway or NodeGateway()
        self.log = logger.new()

    async def collect(self) -> None:
        """Collect nodes statuses and send them to data aggregator
        """
        for node in HATHOR_NODES:
            client = HathorCoreAsyncClient(node)
            node_gateway = NodeGateway(hathor_core_async_client=client)
            await node_gateway.get_node_status_async(self._send)

    def _send(self, data: dict) -> None:
        if 'error' in data:
            self.log.warning("collect_status_error", error=data['error'])
            return
        node = Node.from_status_dict(data)
        self.node_gateway.send_node_to_data_aggregator(node)
