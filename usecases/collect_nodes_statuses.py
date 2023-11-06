from typing import Optional

from common.configuration import HATHOR_NODES
from common.logging import get_logger
from domain.network.node import Node
from gateways.clients.hathor_core_client import HathorCoreAsyncClient
from gateways.node_gateway import NodeGateway

logger = get_logger()


class CollectNodesStatuses:
    """Usecase class to collect nodes statuses"""

    def __init__(self, node_gateway: Optional[NodeGateway] = None) -> None:
        self.node_gateway = node_gateway or NodeGateway()
        self.log = logger.new()

    async def collect(self) -> None:
        """Collect nodes statuses and send them to data aggregator"""
        self.log.info(f"Collecting status from nodes {HATHOR_NODES}")

        for node in HATHOR_NODES:
            client = HathorCoreAsyncClient(node)
            node_gateway = NodeGateway(hathor_core_async_client=client)
            data = await node_gateway.get_node_status_async()
            self._send(data)

    def _send(self, data: dict) -> None:
        if "error" in data:
            self.log.warning("collect_status_error", error=data["error"])
            return
        node = Node.from_status_dict(data)
        # XXX: https://github.com/HathorNetwork/internal-issues/issues/73
        # A big enough known_peers list can reach the limit of data passed to a lambda.
        # This filters the unnecessary peer ids.
        connected_peer_ids = map(lambda p: p.id, node.connected_peers)
        node.known_peers = [
            peer_id for peer_id in connected_peer_ids if peer_id in node.known_peers
        ]
        self.node_gateway.send_node_to_data_aggregator(node)
