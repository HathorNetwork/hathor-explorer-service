from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.network_factory import NetworkFactory
from usecases.aggregate_node_data import AggregateNodeData


class TestAggregateNodeData:

    @fixture
    def node_gateway(self):
        return MagicMock()

    def test_aggregate_no_diff(self, node_gateway):
        network = NetworkFactory()
        node_gateway.aggregate_network = MagicMock(return_value=network)
        node_gateway.get_network = MagicMock(return_value=network)
        node_gateway.save_network = MagicMock()

        aggregate_node_data = AggregateNodeData(node_gateway=node_gateway)

        result = aggregate_node_data.aggregate()

        node_gateway.save_network.assert_not_called()
        assert result

    def test_aggregate_no_old_network(self, node_gateway):
        network = NetworkFactory()
        node_gateway.aggregate_network = MagicMock(return_value=network)
        node_gateway.get_network = MagicMock(return_value=None)
        node_gateway.save_network = MagicMock(return_value=True)

        aggregate_node_data = AggregateNodeData(node_gateway=node_gateway)

        result = aggregate_node_data.aggregate()

        node_gateway.save_network.assert_called_once_with(network)
        assert result

    def test_aggregate_and_save(self, node_gateway):
        network = NetworkFactory()
        network2 = NetworkFactory()
        node_gateway.aggregate_network = MagicMock(return_value=network)
        node_gateway.get_network = MagicMock(return_value=network2)
        node_gateway.save_network = MagicMock()

        aggregate_node_data = AggregateNodeData(node_gateway=node_gateway)

        result = aggregate_node_data.aggregate()

        node_gateway.save_network.assert_called_once_with(network)
        assert result
