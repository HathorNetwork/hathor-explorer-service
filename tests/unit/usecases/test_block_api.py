from unittest.mock import MagicMock

from elasticsearch import exceptions
from pytest import fixture, raises

from common.errors import ApiError
from tests.fixtures.elastic_search_fixtures import GATEWAY_BEST_CHAIN_HEIGHT_SUCCESSFUL_RESPONSE
from usecases.block_api import BlockApi


class TestBlockApi:

    @fixture
    def block_api_gateway(self):
        return MagicMock()

    def test_get_best_chain_height(
        self,
        block_api_gateway,
    ):
        """ Test if API Gateway is being called and if the API GW result is being returned
        """
        block_api_gateway.get_best_chain_height = MagicMock(
            return_value=GATEWAY_BEST_CHAIN_HEIGHT_SUCCESSFUL_RESPONSE
        )

        block_api = BlockApi(block_api_gateway)

        result = block_api.get_best_chain_height()
        block_api_gateway.get_best_chain_height.assert_called_once
        assert result
        assert result == GATEWAY_BEST_CHAIN_HEIGHT_SUCCESSFUL_RESPONSE

    def test_get_best_chain_height_with_exception(self, block_api_gateway):
        """ Check if the ES TransportError is transformed into a API error with the internal_error
        """
        block_api = BlockApi(block_api_gateway)

        block_api_gateway.get_best_chain_height.side_effect = exceptions.TransportError('Boom')

        with raises(ApiError, match='internal_error'):
            block_api.get_best_chain_height()
