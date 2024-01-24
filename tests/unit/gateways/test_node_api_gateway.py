import json
from unittest.mock import MagicMock, patch

from pytest import fixture

from gateways.node_api_gateway import NODE_API_TIMEOUT_IN_SECONDS, NodeApiGateway
from tests.fixtures.node_api_factory import (
    AddressBalanceFactory,
    AddressSearchFactory,
    VersionResourceFactory,
)


class TestNodeApiGateway:
    @fixture
    def cache_client(self):
        return MagicMock()

    @fixture
    def hathor_client(self):
        return MagicMock()

    @patch(
        "gateways.node_api_gateway.ADDRESS_BLACKLIST_COLLECTION_NAME", "mock-collection"
    )
    def test_blacklist_address(self, cache_client):
        cache_client.set = MagicMock(return_value=True)
        gateway = NodeApiGateway(cache_client=cache_client)
        result = gateway.blacklist_address("mock-address")
        cache_client.set.assert_called_once_with("mock-collection", "mock-address", 1)
        assert result is True

    @patch(
        "gateways.node_api_gateway.ADDRESS_BLACKLIST_COLLECTION_NAME", "mock-collection"
    )
    def test_is_blacklisted_address(self, cache_client):
        cache_client.get = MagicMock(return_value="1")
        gateway = NodeApiGateway(cache_client=cache_client)
        result = gateway.is_blacklisted_address("mock-address")
        cache_client.get.assert_called_once_with("mock-collection", "mock-address")
        assert result is True

    @patch("gateways.node_api_gateway.ADDRESS_BALANCE_ENDPOINT", "mock-endpoint")
    def test_get_address_balance(self, hathor_client):
        obj = AddressBalanceFactory()
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_address_balance("mock-address")
        hathor_client.get.assert_called_once_with(
            "mock-endpoint", params={"address": "mock-address"}, timeout=10
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.ADDRESS_BALANCE_ENDPOINT", "mock-endpoint")
    def test_get_address_balance_fail(self, hathor_client):
        hathor_client.get = MagicMock(return_value=None)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_address_balance("mock-address")
        assert result is None

    @patch("gateways.node_api_gateway.ADDRESS_SEARCH_ENDPOINT", "mock-endpoint")
    def test_get_address_search(self, hathor_client):
        obj = AddressSearchFactory()
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_address_search("mock-address", 1)
        hathor_client.get.assert_called_once_with(
            "mock-endpoint", params={"address": "mock-address", "count": 1}, timeout=10
        )
        assert result
        assert sorted(result) == sorted(obj)

        result = gateway.get_address_search("mock-address", 5, token="mock-token")
        hathor_client.get.assert_called_with(
            "mock-endpoint",
            params={"address": "mock-address", "count": 5, "token": "mock-token"},
            timeout=10,
        )
        assert result
        assert sorted(result) == sorted(obj)

        result = gateway.get_address_search(
            "mock-address", 10, hash="a-hash", page="next"
        )
        hathor_client.get.assert_called_with(
            "mock-endpoint",
            params={
                "address": "mock-address",
                "count": 10,
                "hash": "a-hash",
                "page": "next",
            },
            timeout=10,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.ADDRESS_SEARCH_ENDPOINT", "mock-endpoint")
    def test_get_address_search_fail(self, hathor_client):
        hathor_client.get = MagicMock(return_value=None)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_address_search("mock-address", 99)
        assert result is None

    @patch("gateways.node_api_gateway.VERSION_ENDPOINT", "mock-endpoint")
    def test_get_version(self, hathor_client):
        obj = VersionResourceFactory()
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_version()
        hathor_client.get.assert_called_once_with(
            "mock-endpoint", timeout=NODE_API_TIMEOUT_IN_SECONDS
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.DASHBOARD_TX_ENDPOINT", "mock-endpoint")
    def test_get_dashboard_tx(self, hathor_client):
        obj = {"foo": "bar"}
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_dashboard_tx(15, 5)
        hathor_client.get.assert_called_once_with(
            "mock-endpoint",
            params={"tx": 5, "block": 15},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.TX_ACC_WEIGHT_ENDPOINT", "mock-endpoint")
    def test_get_transaction_acc_weight(self, hathor_client):
        obj = {"foo": "bar"}
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_transaction_acc_weight("mock-txid")
        hathor_client.get.assert_called_once_with(
            "mock-endpoint",
            params={"id": "mock-txid"},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.TOKEN_HISTORY_ENDPOINT", "mock-endpoint")
    def test_get_token_history(self, hathor_client):
        obj = {"foo": "bar"}
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_token_history("mock-id-1", 1)
        hathor_client.get.assert_called_once_with(
            "mock-endpoint",
            params={"id": "mock-id-1", "count": 1},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

        result = gateway.get_token_history("mock-id-2", 2, "123")
        hathor_client.get.assert_called_with(
            "mock-endpoint",
            params={
                "id": "mock-id-2",
                "count": 2,
                "hash": "123",
                "page": None,
                "timestamp": None,
            },
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

        result = gateway.get_token_history("mock-id-3", 15, "a-hash", "next", 123)
        hathor_client.get.assert_called_with(
            "mock-endpoint",
            params={
                "id": "mock-id-3",
                "count": 15,
                "hash": "a-hash",
                "page": "next",
                "timestamp": 123,
            },
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.TRANSACTION_ENDPOINT", "mock-endpoint")
    def test_get_transaction(self, hathor_client):
        obj = {"foo": "bar"}
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_transaction("mock-txid")
        hathor_client.get.assert_called_once_with(
            "mock-endpoint",
            params={"id": "mock-txid"},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.FEATURE_ENDPOINT", "mock-endpoint")
    def test_get_feature(self, hathor_client):
        obj = {"foo": "bar"}
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_feature("mock-block")
        hathor_client.get.assert_called_once_with(
            "mock-endpoint",
            params={"block": "mock-block"},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.TRANSACTION_ENDPOINT", "mock-endpoint")
    def test_list_transactions(self, hathor_client):
        obj = {"foo": "bar"}
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.list_transactions("type-1", 1)
        hathor_client.get.assert_called_once_with(
            "mock-endpoint",
            params={"type": "type-1", "count": 1},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

        result = gateway.list_transactions("type-2", 2, "123")
        hathor_client.get.assert_called_with(
            "mock-endpoint",
            params={
                "type": "type-2",
                "count": 2,
                "hash": "123",
                "page": None,
                "timestamp": None,
            },
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

        result = gateway.list_transactions("type-3", 15, "a-hash", "next", 123)
        hathor_client.get.assert_called_with(
            "mock-endpoint",
            params={
                "type": "type-3",
                "count": 15,
                "hash": "a-hash",
                "page": "next",
                "timestamp": 123,
            },
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.TOKEN_ENDPOINT", "mock-endpoint")
    def test_get_token(self, hathor_client):
        obj = {"foo": "bar"}
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_token("mock-token-uid")
        hathor_client.get.assert_called_once_with(
            "mock-endpoint",
            params={"id": "mock-token-uid"},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.DECODE_TX_ENDPOINT", "mock-endpoint")
    def test_decode_tx(self, hathor_client):
        obj = {"foo": "bar"}
        hathor_client.get = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.decode_tx("hex-tx-data")
        hathor_client.get.assert_called_once_with(
            "mock-endpoint",
            params={"hex_tx": "hex-tx-data"},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.PUSH_TX_ENDPOINT", "mock-endpoint")
    def test_push_tx(self, hathor_client):
        obj = {"foo": "bar"}
        hathor_client.post = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.push_tx("hex-tx-data")
        hathor_client.post.assert_called_once_with(
            "mock-endpoint",
            body={"hex_tx": "hex-tx-data"},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
        assert result
        assert sorted(result) == sorted(obj)

    @patch("gateways.node_api_gateway.GRAPHVIZ_DOT_NEIGHBORS_ENDPOINT", "mock-endpoint")
    def test_graphviz_dot_neighbors(self, hathor_client):
        obj = json.dumps({"foo": "bar"})
        data = {
            "tx": "123",
            "graph_type": "456",
            "max_level": 789,
        }
        hathor_client.get_text = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.graphviz_dot_neighbors(**data)
        hathor_client.get_text.assert_called_once_with(
            "mock-endpoint", params=data, timeout=NODE_API_TIMEOUT_IN_SECONDS
        )
        assert result
        assert result == obj

    @patch("gateways.node_api_gateway.NC_STATE_ENDPOINT", "mock-endpoint")
    def test_nc_state(self, hathor_client):
        obj = json.dumps({"foo": "bar"})
        data = {
            "id": "1234",
            "fields[]": ["field1", "field2"],
            "balances[]": ["balance1"],
            "calls[]": ["call1()", "call2(arg1, arg2)"],
        }
        hathor_client.get_text = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_nc_state(**data)
        hathor_client.get_text.assert_called_once_with(
            "mock-endpoint", params=data, timeout=NODE_API_TIMEOUT_IN_SECONDS
        )
        assert result
        assert result == obj

    @patch("gateways.node_api_gateway.NC_HISTORY_ENDPOINT", "mock-endpoint")
    def test_nc_history(self, hathor_client):
        obj = json.dumps({"foo": "bar"})
        data = {
            "id": "1234",
        }
        hathor_client.get_text = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_nc_history(**data)
        hathor_client.get_text.assert_called_once_with(
            "mock-endpoint", params=data, timeout=NODE_API_TIMEOUT_IN_SECONDS
        )
        assert result
        assert result == obj

    @patch(
        "gateways.node_api_gateway.NC_BLUEPRINT_INFORMATION_ENDPOINT", "mock-endpoint"
    )
    def test_nc_blueprint_information(self, hathor_client):
        obj = json.dumps({"foo": "bar"})
        data = {
            "blueprint_id": "1234",
        }
        hathor_client.get_text = MagicMock(return_value=obj)
        gateway = NodeApiGateway(hathor_core_client=hathor_client)
        result = gateway.get_nc_blueprint_information(**data)
        hathor_client.get_text.assert_called_once_with(
            "mock-endpoint", params=data, timeout=NODE_API_TIMEOUT_IN_SECONDS
        )
        assert result
        assert result == obj
