from unittest.mock import MagicMock, patch

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

    @patch("usecases.collect_nodes_statuses.HATHOR_NODES", ["a", "b"])
    async def test_collect(self, node_gateway):
        node = Node.from_status_dict(HATHOR_CORE_MAINNET_GET_STATUS)
        # XXX: filtering known_peers based on connected_peers
        connected_peer_ids = map(lambda p: p.id, node.connected_peers)
        node.known_peers = [
            peer_id for peer_id in connected_peer_ids if peer_id in node.known_peers
        ]

        node_gateway.get_node_status_async = AsyncMock(
            side_effect=lambda: HATHOR_CORE_MAINNET_GET_STATUS
        )
        with patch.object(
            NodeGateway, "get_node_status_async", new=node_gateway.get_node_status_async
        ):
            node_gateway.send_node_to_data_aggregator = MagicMock()

            usecase = CollectNodesStatuses(node_gateway)
            await usecase.collect()

            node_gateway.get_node_status_async.assert_called()
            node_gateway.send_node_to_data_aggregator.assert_called_with(node)

    @patch("usecases.collect_nodes_statuses.HATHOR_NODES", ["a", "b"])
    async def test_collect_skips_error_body_without_error_key(self, node_gateway):
        """A 5xx JSON body without "error" is skipped and the next node still runs."""
        error_body = {"message": "fullnode overloaded"}
        responses = iter([error_body, HATHOR_CORE_MAINNET_GET_STATUS])
        node_gateway.get_node_status_async = AsyncMock(
            side_effect=lambda: next(responses)
        )
        with patch.object(
            NodeGateway, "get_node_status_async", new=node_gateway.get_node_status_async
        ):
            node_gateway.send_node_to_data_aggregator = MagicMock()

            usecase = CollectNodesStatuses(node_gateway)
            with patch.object(usecase, "log") as mock_log:
                await usecase.collect()

            assert node_gateway.get_node_status_async.call_count == 2
            node_gateway.send_node_to_data_aggregator.assert_called_once()
            mock_log.warning.assert_called_once_with(
                "collect_status_error",
                error="KeyError('known_peers')",
                data=str(error_body),
            )
