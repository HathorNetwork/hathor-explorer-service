import json
from unittest.mock import MagicMock

from pytest import fixture

from usecases.token_balances_api import TokenBalancesApi


class TestMetadata:
    @fixture
    def token_balances_api_gateway(self):
        return MagicMock()

    def test_get_token_balances(self, token_balances_api_gateway):
        token_balances_api_gateway.get_token_balances = MagicMock(
            return_value="some-return"
        )

        token_balances_api = TokenBalancesApi(token_balances_api_gateway)

        result = token_balances_api.get_token_balances(
            "tokenA", "sort-by-this", "with-this-order", ["search", "after", "this"]
        )

        token_balances_api_gateway.get_token_balances.assert_called_once_with(
            "tokenA", "sort-by-this", "with-this-order", ["search", "after", "this"]
        )
        assert result == "some-return"

    def test_get_token_information(self, token_balances_api_gateway):
        token_balances_api_gateway.get_token_information = MagicMock(
            return_value="some-return"
        )

        token_balances_api = TokenBalancesApi(token_balances_api_gateway)

        result = token_balances_api.get_token_information("tokenB")

        token_balances_api_gateway.get_token_information.assert_called_once_with(
            "tokenB"
        )
        assert result == "some-return"
