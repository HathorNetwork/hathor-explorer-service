from typing import Union

from common.configuration import HATHOR_NODES
from domain.network.node import Node
from gateways.aws.lambda_gateway import LambdaGateway
from gateways.hathor.hathor_core_client import HathorCoreAsyncClient
from gateways.hathor.hathor_core_gateway import HathorCoreGateway


class CollectNodesStatuses:

    def __init__(self, lambda_gateway: Union[LambdaGateway, None] = None) -> None:
        self.lambda_gateway = lambda_gateway or LambdaGateway()

    async def collect(self) -> None:
        for node in HATHOR_NODES:
            client = HathorCoreAsyncClient(node)
            hathor_core_gateway = HathorCoreGateway(async_client=client)
            await hathor_core_gateway.get_async('/v1a/status', self._send)

    def _send(self, data: dict) -> None:
        network = Node.from_status_dict(data)
        self.lambda_gateway.send_node_to_data_aggregator(network)
