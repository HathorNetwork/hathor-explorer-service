from unittest.mock import MagicMock, patch

from pytest import fixture

from gateways.node_api_gateway import NodeApiGateway
from tests.fixtures.node_api_factory import AddressBalanceFactory, AddressSearchFactory


class TestNodeApiGateway:

    @fixture
    def cache_client(self):
        return MagicMock()

    @fixture
    def hathor_client(self):
        return MagicMock()

    @patch('gateways.node_api_gateway.ADDRESS_BLACKLIST_COLLECTION_NAME', 'mock-collection')
    def test_blacklist_address(self, cache_client):
        cache_client.set = MagicMock(return_value=True)
        gateway = NodeApiGateway(cache_client=cache_client)
        result = gateway.blacklist_address('mock-address')
        cache_client.set.assert_called_once_with('mock-collection', 'mock-address', 1)
        assert result is True

    @patch('gateways.node_api_gateway.ADDRESS_BLACKLIST_COLLECTION_NAME', 'mock-collection')
    def test_is_blacklisted_address(self, cache_client):
        cache_client.get = MagicMock(return_value='1')
        gateway = NodeApiGateway(cache_client=cache_client)
        result = gateway.is_blacklisted_address('mock-address')
        cache_client.get.assert_called_once_with('mock-collection', 'mock-address')
        assert result is True

    @patch('gateways.node_api_gateway.ADDRESS_BALANCE_ENDPOINT', 'mock-endpoint')
    def test_get_address_balance(self, hathor_client):
        obj = AddressBalanceFactory()
        hathor_client.get = MagicMock(return_value=obj.to_dict())
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_address_balance('mock-address')
        hathor_client.get.assert_called_once_with('mock-endpoint', params={'address': 'mock-address'}, timeout=10)
        assert result
        assert result.success == obj.success
        assert result.total_transactions == obj.total_transactions

    @patch('gateways.node_api_gateway.ADDRESS_SEARCH_ENDPOINT', 'mock-endpoint')
    def test_get_address_search(self, hathor_client):
        obj = AddressSearchFactory()
        hathor_client.get = MagicMock(return_value=obj.to_dict())
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_address_search('mock-address', 1)
        hathor_client.get.assert_called_once_with(
                'mock-endpoint', params={'address': 'mock-address', 'count': 1}, timeout=10)
        assert result
        assert result.success == obj.success

        result = gateway.get_address_search('mock-address', 5, token='mock-token')
        hathor_client.get.assert_called_with(
                'mock-endpoint', params={'address': 'mock-address', 'count': 5, 'token': 'mock-token'}, timeout=10)
        assert result
        assert result.success == obj.success

        result = gateway.get_address_search('mock-address', 10, hash='a-hash', page='next')
        hathor_client.get.assert_called_with(
                'mock-endpoint',
                params={
                    'address': 'mock-address',
                    'count': 10,
                    'hash': 'a-hash',
                    'page': 'next'},
                timeout=10)
        assert result
        assert result.success == obj.success
