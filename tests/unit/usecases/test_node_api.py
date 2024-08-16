from unittest.mock import MagicMock, patch

from pytest import fixture, raises

from common.errors import HathorCoreTimeout
from tests.fixtures.node_api_factory import (
    AddressBalanceFactory,
    AddressSearchFactory,
    VersionResourceFactory,
)
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
        result = node_api.get_address_balance("fake-address")
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_balance.assert_called_once_with("fake-address")
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert sorted(result) == sorted(obj)

    def test_address_balance_none(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(return_value=None)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance("fake-address")
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_balance.assert_called_once_with("fake-address")
        node_api_gateway.blacklist_address.assert_not_called()
        assert result is None

    def test_address_balance_fail(self, node_api_gateway):
        obj = AddressBalanceFactory(fail=True)
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance("fake-address")
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_balance.assert_called_once_with("fake-address")
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert sorted(result) == sorted(obj)

    @patch("usecases.node_api.ADDRESS_BLACKLIST_RESPONSE", "mock-response")
    def test_address_balance_timeout(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(
            side_effect=HathorCoreTimeout("timeout")
        )
        node_api_gateway.blacklist_address = MagicMock(return_value=None)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance("fake-address")
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_balance.assert_called_once_with("fake-address")
        node_api_gateway.blacklist_address.assert_called_once_with("fake-address")
        assert result
        assert result == "mock-response"

    @patch("usecases.node_api.ADDRESS_BLACKLIST_RESPONSE", "mock-response")
    def test_address_balance_blacklisted(self, node_api_gateway):
        obj = AddressBalanceFactory()
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=True)
        node_api_gateway.get_address_balance = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_balance("fake-address")
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_balance.assert_not_called()
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert result == "mock-response"

    def test_address_balance_reraise(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_balance = MagicMock(
            side_effect=Exception("not timeout")
        )

        node_api = NodeApi(node_api_gateway)
        with raises(Exception, match=r"not timeout"):
            node_api.get_address_balance("fake-address")
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")


class TestNodeApiAddressSearch:
    @fixture
    def node_api_gateway(self):
        return MagicMock()

    def test_address_search_ok(self, node_api_gateway):
        obj = AddressSearchFactory()
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search("fake-address", 1)
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_search.assert_called_once_with(
            "fake-address", 1, None, None, None
        )
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert sorted(result) == sorted(obj)

    def test_address_search_none(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(return_value=None)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search("fake-address", 50)
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_search.assert_called_once_with(
            "fake-address", 50, None, None, None
        )
        node_api_gateway.blacklist_address.assert_not_called()
        assert result is None

    def test_address_search_fail(self, node_api_gateway):
        obj = AddressSearchFactory(fail=True)
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(return_value=obj)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search("fake-address", 5)
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_search.assert_called_once_with(
            "fake-address", 5, None, None, None
        )
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert sorted(result) == sorted(obj)

    @patch("usecases.node_api.ADDRESS_BLACKLIST_RESPONSE", "mock-response")
    def test_address_search_timeout(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(
            side_effect=HathorCoreTimeout("timeout")
        )
        node_api_gateway.blacklist_address = MagicMock(return_value=None)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search("fake-address", 10)
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_search.assert_called_once_with(
            "fake-address", 10, None, None, None
        )
        node_api_gateway.blacklist_address.assert_called_once_with("fake-address")
        assert result
        assert result == "mock-response"

    @patch("usecases.node_api.ADDRESS_BLACKLIST_RESPONSE", "mock-response")
    def test_address_search_blacklisted(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=True)

        node_api = NodeApi(node_api_gateway)
        result = node_api.get_address_search("fake-address", 20)
        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")
        node_api_gateway.get_address_search.assert_not_called()
        node_api_gateway.blacklist_address.assert_not_called()
        assert result
        assert result == "mock-response"

    def test_address_search_reraise(self, node_api_gateway):
        node_api_gateway.is_blacklisted_address = MagicMock(return_value=False)
        node_api_gateway.get_address_search = MagicMock(
            side_effect=Exception("not timeout")
        )

        node_api = NodeApi(node_api_gateway)
        with raises(Exception, match=r"not timeout"):
            node_api.get_address_search("fake-address", 15)

        node_api_gateway.is_blacklisted_address.assert_called_once_with("fake-address")


class TestNodeApiCommon:
    @fixture
    def node_api_gateway(self):
        return MagicMock()

    def test_version(self, node_api_gateway):
        obj = VersionResourceFactory()
        node_api_gateway.get_version = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_version()
        node_api_gateway.get_version.assert_called_once()
        assert result
        assert sorted(result) == sorted(obj)

    def test_dashboard_tx(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_dashboard_tx = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_dashboard_tx(50, 4)
        node_api_gateway.get_dashboard_tx.assert_called_once_with(50, 4)
        assert result
        assert sorted(result) == sorted(obj)

    def test_get_transaction_acc_weight(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_transaction_acc_weight = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_transaction_acc_weight("mock-txid")
        node_api_gateway.get_transaction_acc_weight.assert_called_once_with("mock-txid")
        assert result
        assert sorted(result) == sorted(obj)

    def test_get_token_history(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_token_history = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_token_history("mock-token-uid", 1)
        node_api_gateway.get_token_history.assert_called_once_with(
            "mock-token-uid", 1, None, None, None
        )
        assert result
        assert sorted(result) == sorted(obj)

        result = node_api.get_token_history(
            "mock-token-uid-2", 10, "a-hash", "a-page", 8765
        )
        node_api_gateway.get_token_history.assert_called_with(
            "mock-token-uid-2", 10, "a-hash", "a-page", 8765
        )
        assert result
        assert sorted(result) == sorted(obj)

    def test_get_transaction(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_transaction = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_transaction("mock-tx-id")
        node_api_gateway.get_transaction.assert_called_once_with("mock-tx-id")
        assert result
        assert sorted(result) == sorted(obj)

    def test_get_feature(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_feature = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_feature("mock-block")
        node_api_gateway.get_feature.assert_called_once_with("mock-block")
        assert result
        assert sorted(result) == sorted(obj)

    def test_list_transactions(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.list_transactions = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.list_transactions("mock-tx-id", 27)
        node_api_gateway.list_transactions.assert_called_once_with(
            "mock-tx-id", 27, None, None, None
        )
        assert result
        assert sorted(result) == sorted(obj)

        result = node_api.list_transactions(
            "mock-tx-id-2", 81, "a-hash", "a-page", 8765
        )
        node_api_gateway.list_transactions.assert_called_with(
            "mock-tx-id-2", 81, "a-hash", "a-page", 8765
        )
        assert result
        assert sorted(result) == sorted(obj)

    def test_get_token(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_token = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_token("mock-tx-id")
        node_api_gateway.get_token.assert_called_once_with("mock-tx-id")
        assert result
        assert sorted(result) == sorted(obj)

    def test_decode_tx(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.decode_tx = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.decode_tx("mock-tx-hex")
        node_api_gateway.decode_tx.assert_called_once_with("mock-tx-hex")
        assert result
        assert sorted(result) == sorted(obj)

    def test_push_tx(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.push_tx = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.push_tx("mock-tx-hex")
        node_api_gateway.push_tx.assert_called_once_with("mock-tx-hex")
        assert result
        assert sorted(result) == sorted(obj)

    def test_graphviz_dot_neighbors(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.graphviz_dot_neighbors = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.graphviz_dot_neighbors("123", "456", 789)
        node_api_gateway.graphviz_dot_neighbors.assert_called_once_with(
            "123", "456", 789
        )
        assert result
        assert sorted(result) == sorted(obj)


class TestNodeApiNanoContracts:
    @fixture
    def node_api_gateway(self):
        return MagicMock()

    def test_get_state(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_nc_state = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_nc_state(
            "1234", ["field1", "field2"], ["balance1"], ["call1()", "call2(arg1, arg2)"]
        )
        node_api_gateway.get_nc_state.assert_called_once_with(
            "1234", ["field1", "field2"], ["balance1"], ["call1()", "call2(arg1, arg2)"]
        )
        assert result
        assert sorted(result) == sorted(obj)

    def test_get_history_after(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_nc_history = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_nc_history("1234", "5678", None, 100)
        node_api_gateway.get_nc_history.assert_called_once_with("1234", "5678", None, 100)
        assert result
        assert sorted(result) == sorted(obj)

    def test_get_history_before(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_nc_history = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_nc_history("1234", None, "5678", 100)
        node_api_gateway.get_nc_history.assert_called_once_with("1234", None, "5678", 100)
        assert result
        assert sorted(result) == sorted(obj)

    def test_get_history_without_optional(self, node_api_gateway):
        # Now only with required parameter
        obj = {"foo": "bar"}
        node_api_gateway.get_nc_history = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_nc_history("1234")
        node_api_gateway.get_nc_history.assert_called_once_with("1234", None, None, None)
        assert result
        assert sorted(result) == sorted(obj)

    def test_get_blueprint_information(self, node_api_gateway):
        obj = {"foo": "bar"}
        node_api_gateway.get_nc_blueprint_information = MagicMock(return_value=obj)
        node_api = NodeApi(node_api_gateway)
        result = node_api.get_nc_blueprint_information("1234")
        node_api_gateway.get_nc_blueprint_information.assert_called_once_with("1234")
        assert result
        assert sorted(result) == sorted(obj)
