from tests.fixtures.node_factory import NodeFactory
from gateways.cache.cache_gateway import CacheGateway
from unittest.mock import MagicMock

from pytest import fixture


class TestCacheGateway:

    @fixture
    def cache_client(self):
        return MagicMock()

    def test_save_netowrk(self, cache_client):
        cache_client.set = MagicMock(return_value=True)

        gateway = CacheGateway(cache_client)
        node = NodeFactory()
        id = node.id

        result = gateway.save_node(id, node)

        cache_client.set.assert_called_once_with('node', id, node.to_dict())
        assert result

    def test_get_node(self, cache_client):
        node = NodeFactory()
        id = node.id
        cache_client.get = MagicMock(return_value=node.to_dict())

        gateway = CacheGateway(cache_client)

        result = gateway.get_node(id)

        cache_client.get.assert_called_once_with('node', id)
        assert result
        assert result.id == id

    def test_get_no_node(self, cache_client):
        cache_client.get = MagicMock(return_value=None)

        gateway = CacheGateway(cache_client)

        result = gateway.get_node('abc123')

        cache_client.get.assert_called_once_with('node', 'abc123')
        assert result is None

    def test_list_node_keys(self, cache_client):
        keys = ['alderaan', 'dagobah', 'jakku', 'naboo', 'tatooine']
        cache_client.keys = MagicMock(return_value=keys)

        gateway = CacheGateway(cache_client)

        result = gateway.list_node_keys()

        cache_client.keys.assert_called_once_with('node')
        assert result == keys
