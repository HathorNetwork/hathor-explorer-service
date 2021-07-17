from unittest.mock import MagicMock, patch

import pytest
from pytest import fixture

from gateways.node_gateway import NodeGateway
from tests.fixtures.node_factory import NodeFactory
from tests.fixtures.network_factory import NetworkFactory


class TestNodeGateway:

    @fixture
    def lambda_client(self):
        return MagicMock()

    @fixture
    def cache_client(self):
        return MagicMock()

    @fixture
    def hathor_core_async_client(self):
        return MagicMock()

    @patch('gateways.node_gateway.DATA_AGGREGATOR_LAMBDA_NAME', 'data-aggregator')
    def test_node_to_data_aggregator(self, lambda_client):
        lambda_client.invoke_async = MagicMock(return_value=202)

        gateway = NodeGateway(lambda_client=lambda_client)

        node_data = NodeFactory()
        result = gateway.send_node_to_data_aggregator(node_data)

        lambda_client.invoke_async.assert_called_once_with('data-aggregator', node_data.to_dict())
        assert result == 202

    @patch('gateways.node_gateway.DATA_AGGREGATOR_LAMBDA_NAME', None)
    def test_node_to_data_aggregator_error(self, lambda_client):
        gateway = NodeGateway(lambda_client=lambda_client)
        node_data = NodeFactory()

        with pytest.raises(Exception, match=r'No lambda name in config'):
            gateway.send_node_to_data_aggregator(node_data)

    @patch('gateways.node_gateway.NODE_CACHE_TTL', 30)
    def test_save_node(self, cache_client):
        cache_client.set = MagicMock(return_value=True)

        gateway = NodeGateway(cache_client=cache_client)
        node = NodeFactory()
        id = node.id

        result = gateway.save_node(id, node)

        cache_client.set.assert_called_once_with('node', id, node.to_dict(), 30)
        assert result

    def test_get_node(self, cache_client):
        node = NodeFactory()
        id = node.id
        cache_client.get = MagicMock(return_value=node.to_dict())

        gateway = NodeGateway(cache_client=cache_client)

        result = gateway.get_node(id)

        cache_client.get.assert_called_once_with('node', id)
        assert result
        assert result.id == id

    def test_get_no_node(self, cache_client):
        cache_client.get = MagicMock(return_value=None)

        gateway = NodeGateway(cache_client=cache_client)

        result = gateway.get_node('abc123')

        cache_client.get.assert_called_once_with('node', 'abc123')
        assert result is None

    def test_list_node_keys(self, cache_client):
        keys = ['alderaan', 'dagobah', 'jakku', 'naboo', 'tatooine']
        cache_client.keys = MagicMock(return_value=keys)

        gateway = NodeGateway(cache_client=cache_client)

        result = gateway.list_node_keys()

        cache_client.keys.assert_called_once_with('node')
        assert result == keys

    def test_save_network(self, cache_client):
        cache_client.set = MagicMock(return_value=True)

        gateway = NodeGateway(cache_client=cache_client)
        network = NetworkFactory()

        result = gateway.save_network(id, network)

        cache_client.set.assert_called_once_with('network', 'v1', network.to_dict())
        assert result
