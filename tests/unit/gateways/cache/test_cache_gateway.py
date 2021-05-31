from tests.fixtures.network_factory import NetworkFactory
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
        network = NetworkFactory()
        id = network.id

        result = gateway.save_network(id, network)

        cache_client.set.assert_called_once_with('network', id, network.to_dict())
        assert result

    def test_get_network(self, cache_client):
        network = NetworkFactory()
        id = network.id
        cache_client.get = MagicMock(return_value=network.to_dict())

        gateway = CacheGateway(cache_client)

        result = gateway.get_network(id)

        cache_client.get.assert_called_once_with('network', id)
        assert result
        assert result.id == id

    def test_get_no_network(self, cache_client):
        cache_client.get = MagicMock(return_value=None)

        gateway = CacheGateway(cache_client)

        result = gateway.get_network('abc123')

        cache_client.get.assert_called_once_with('network', 'abc123')
        assert result is None

    def test_list_network_keys(self, cache_client):
        keys = ['alderaan', 'dagobah', 'jakku', 'naboo', 'tatooine']
        cache_client.keys = MagicMock(return_value=keys)

        gateway = CacheGateway(cache_client)

        result = gateway.list_network_keys()

        cache_client.keys.assert_called_once_with('network')
        assert result == keys
