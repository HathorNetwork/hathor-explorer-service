from unittest.mock import MagicMock, patch

from pytest import fixture, raises

from common.errors import HathorCoreTimeout
from tests.fixtures.node_api_factory import AddressBalanceFactory, AddressSearchFactory
from usecases.node_api import NodeApi


class TestNodeApiAddressBalance:

    @fixture
    def node_api_gateway(self):
        return MagicMock()

    def test_address_balance_ok(self, node_api_gateway):
        obj = AddressBalanceFactory()
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')
        node_api_gateway.get_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert sorted(result) == sorted(obj)

    def test_address_balance_fail(self, node_api_gateway):
        obj = AddressBalanceFactory(fail=True)
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')
        node_api_gateway.get_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert sorted(result) == sorted(obj)

    @patch('usecases.node_api.ADDRESS_BLACKLIST_RESPONSE', 'mock-response')
    def test_address_balance_timeout(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(side_effect=HathorCoreTimeout('timeout'))
        node_api_gateway.blacklist_address = MagicMock(return_value=None)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')
        node_api_gateway.get_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.blacklist_address.assert_called_once_with('fake-address')
        assert result
        assert result == 'mock-response'

    @patch('usecases.node_api.ADDRESS_BLACKLIST_RESPONSE', 'mock-response')
    def test_address_balance_blacklisted(self, node_api_gateway):
        obj = AddressBalanceFactory()
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=True)
        node_api_gateway.get_address_balance = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')
        node_api_gateway.get_address_balance.assert_not_called()
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert result == 'mock-response'

    def test_address_balance_reraise(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(side_effect=Exception('not timeout'))

        node_api = NodeApi(node_api_gateway)
        with raises(Exception, match=r'not timeout'):
            node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')


class TestNodeApiAddressSearch:

    @fixture
    def node_api_gateway(self):
        return MagicMock()

    def test_address_search_ok(self, node_api_gateway):
        obj = AddressSearchFactory()
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search('fake-address', 1)
        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')
        node_api_gateway.get_address_search.assert_called_once_with('fake-address', 1, None, None, None)
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert sorted(result) == sorted(obj)

    def test_address_search_fail(self, node_api_gateway):
        obj = AddressSearchFactory(fail=True)
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search('fake-address', 5)
        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')
        node_api_gateway.get_address_search.assert_called_once_with('fake-address', 5, None, None, None)
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert sorted(result) == sorted(obj)

    @patch('usecases.node_api.ADDRESS_BLACKLIST_RESPONSE', 'mock-response')
    def test_address_search_timeout(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(side_effect=HathorCoreTimeout('timeout'))
        node_api_gateway.blacklist_address = MagicMock(return_value=None)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search('fake-address', 10)
        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')
        node_api_gateway.get_address_search.assert_called_once_with('fake-address', 10, None, None, None)
        node_api_gateway.blacklist_address.assert_called_once_with('fake-address')
        assert result
        assert result == 'mock-response'

    @patch('usecases.node_api.ADDRESS_BLACKLIST_RESPONSE', 'mock-response')
    def test_address_search_blacklisted(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=True)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search('fake-address', 20)
        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')
        node_api_gateway.get_address_search.assert_not_called()
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert result == 'mock-response'

    def test_address_search_reraise(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(side_effect=Exception('not timeout'))

        node_api = NodeApi(node_api_gateway)
        with raises(Exception, match=r'not timeout'):
            node_api.get_address_search('fake-address', 15)

        node_api_gateway.is_blacklisted_address.assert_called_once_with('fake-address')
