from unittest.mock import MagicMock

from pytest import fixture, raises

from tests.fixtures.node_api_factory import AddressBalanceFactory, AddressSearchFactory
from usecases.node_api import NodeApi


class TestNodeApiAddressBalance:

    @fixture
    def node_api_gateway(self):
        return MagicMock()

    def test_address_balance_ok(self, node_api_gateway):
        obj = AddressBalanceFactory()
        node_api_gateway.is_blacklisted_address_balance = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.get_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.blacklist_address_balance.assert_not_called()
        assert result
        assert result['success'] is True
        assert result['total_transactions'] == obj.total_transactions
        assert sorted(result['tokens_data']) == sorted(obj.tokens_data)
        assert 'message' not in result

    def test_address_balance_fail(self, node_api_gateway):
        obj = AddressBalanceFactory(fail=True)
        node_api_gateway.is_blacklisted_address_balance = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.get_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.blacklist_address_balance.assert_not_called()
        assert result
        assert result['success'] is False
        assert result['message'] == obj.message
        assert result['total_transactions'] is None
        assert result['total_transactions'] == obj.total_transactions
        assert result['tokens_data'] is None
        assert result['tokens_data'] == obj.tokens_data

    def test_address_balance_timeout(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address_balance = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(side_effect=Exception('timeout'))
        node_api_gateway.blacklist_address_balance = MagicMock(return_value=None)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.get_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.blacklist_address_balance.assert_called_once_with('fake-address')
        assert result
        assert result['success'] is False
        assert result['message'] == 'address blacklisted'

    def test_address_balance_blacklisted(self, node_api_gateway):
        obj = AddressBalanceFactory()
        node_api_gateway.is_blacklisted_address_balance = MagicMock(return_value=True)
        node_api_gateway.get_address_balance = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address_balance.assert_called_once_with('fake-address')
        node_api_gateway.get_address_balance.assert_not_called()
        node_api_gateway.blacklist_address_balance.assert_not_called()
        assert result
        assert result['success'] is False
        assert result['message'] == 'address blacklisted'

    def test_address_balance_reraise(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address_balance = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(side_effect=Exception('not timeout'))

        node_api = NodeApi(node_api_gateway)
        with raises(Exception, match=r'not timeout'):
            node_api.get_address_balance('fake-address')
        node_api_gateway.is_blacklisted_address_balance.assert_called_once_with('fake-address')


class TestNodeApiAddressSearch:

    @fixture
    def node_api_gateway(self):
        return MagicMock()

    def test_address_search_ok(self, node_api_gateway):
        obj = AddressSearchFactory()
        node_api_gateway.is_blacklisted_address_search = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search('fake-address', 1)
        node_api_gateway.is_blacklisted_address_search.assert_called_once_with('fake-address')
        node_api_gateway.get_address_search.assert_called_once_with('fake-address', 1, None, None, None)
        node_api_gateway.blacklist_address_search.assert_not_called()
        assert result
        assert result['success'] is True
        assert result['has_more'] == obj.has_more
        assert result['total'] == obj.total
        assert 'message' not in result

    def test_address_search_fail(self, node_api_gateway):
        obj = AddressSearchFactory(fail=True)
        node_api_gateway.is_blacklisted_address_search = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search('fake-address', 5)
        node_api_gateway.is_blacklisted_address_search.assert_called_once_with('fake-address')
        node_api_gateway.get_address_search.assert_called_once_with('fake-address', 5, None, None, None)
        node_api_gateway.blacklist_address_search.assert_not_called()
        assert result
        assert result['success'] is False
        assert result['message'] == obj.message
        assert result['total'] is None
        assert result['total'] == obj.total
        assert result['has_more'] is None
        assert result['has_more'] == obj.has_more

    def test_address_search_timeout(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address_search = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(side_effect=Exception('timeout'))
        node_api_gateway.blacklist_address_search = MagicMock(return_value=None)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search('fake-address', 10)
        node_api_gateway.is_blacklisted_address_search.assert_called_once_with('fake-address')
        node_api_gateway.get_address_search.assert_called_once_with('fake-address', 10, None, None, None)
        node_api_gateway.blacklist_address_search.assert_called_once_with('fake-address')
        assert result
        assert result['success'] is False
        assert result['message'] == 'address blacklisted'

    def test_address_search_blacklisted(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address_search = MagicMock(return_value=True)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search('fake-address', 20)
        node_api_gateway.is_blacklisted_address_search.assert_called_once_with('fake-address')
        node_api_gateway.get_address_search.assert_not_called()
        node_api_gateway.blacklist_address_search.assert_not_called()
        assert result
        assert result['success'] is False
        assert result['message'] == 'address blacklisted'

    def test_address_search_reraise(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address_search = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(side_effect=Exception('not timeout'))

        node_api = NodeApi(node_api_gateway)
        with raises(Exception, match=r'not timeout'):
            node_api.get_address_search('fake-address', 15)

        node_api_gateway.is_blacklisted_address_search.assert_called_once_with('fake-address')
