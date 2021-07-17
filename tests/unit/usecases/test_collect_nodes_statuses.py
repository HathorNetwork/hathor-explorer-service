from datetime import datetime
from unittest.mock import MagicMock, patch

from freezegun import freeze_time
from pytest import fixture

from domain.network.node import Node
from gateways.node_gateway import NodeGateway
from tests.fixtures.hathor_core_fixtures import HATHOR_CORE_MAINNET_GET_STATUS
from usecases.collect_nodes_statuses import CollectNodesStatuses


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


class TestCollectNodesStatuses:

    @fixture
    def node_gateway(self):
        return MagicMock()

    @patch('usecases.collect_nodes_statuses.HATHOR_NODES', ['a', 'b'])
    @freeze_time(datetime.now())
    async def test_collect(self, node_gateway):
        node = Node.from_status_dict(HATHOR_CORE_MAINNET_GET_STATUS)

        node_gateway.get_node_status_async = AsyncMock(side_effect=lambda x: x(HATHOR_CORE_MAINNET_GET_STATUS))
        with patch.object(NodeGateway, 'get_node_status_async', new=node_gateway.get_node_status_async):
            node_gateway.send_node_to_data_aggregator = MagicMock()

            usecase = CollectNodesStatuses(node_gateway)
            await usecase.collect()

            node_gateway.get_node_status_async.assert_called()
            node_gateway.send_node_to_data_aggregator.assert_called_with(node)
