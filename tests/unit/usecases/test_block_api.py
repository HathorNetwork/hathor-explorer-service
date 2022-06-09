from unittest.mock import MagicMock

from tests.fixtures.elastic_search_fixtures import GATEWAY_BIGGEST_HEIGHT_SUCCESSFUL_RESPONSE

from pytest import fixture

from usecases.block_api import BlockApi

class TestBlockApi:

    @fixture
    def block_api_gateway(self):
        return MagicMock()

    def test_get_block_with_biggest_height(
        self,
        block_api_gateway,
    ):
        """ Test if API Gateway is being called and if the API GW result is being returned
        """
        block_api_gateway.get_block_with_biggest_height = MagicMock(
            return_value = GATEWAY_BIGGEST_HEIGHT_SUCCESSFUL_RESPONSE
        )

        block_api = BlockApi(block_api_gateway)

        result = block_api.get_block_with_biggest_height()
        block_api_gateway.get_block_with_biggest_height.assert_called_once
        assert result
        assert result == GATEWAY_BIGGEST_HEIGHT_SUCCESSFUL_RESPONSE
