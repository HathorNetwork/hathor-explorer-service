from unittest.mock import MagicMock

from pytest import fixture

from usecases.block_api import BlockApi

API_GATEWAY_GET_BLOCK_WITH_BIGGEST_HEIGHT_RESPONSE = {
    'hits':
    [
        {
            'tx_id': '00a1786694f2b2248c4272e64f9f414759322b4e6d5e40d39cc5b5aedfd70dfb',
            'timestamp': '2022-05-09T18:55:47Z',
            'version': 0,
            'voided': False,
            'height': 1740645,
            'weight': 60.66999816894531,
            'hash_rate': 123
        }
    ],
    'has_next': False
}


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
            return_value=API_GATEWAY_GET_BLOCK_WITH_BIGGEST_HEIGHT_RESPONSE
        )

        block_api = BlockApi(block_api_gateway)

        result = block_api.get_block_with_biggest_height()
        block_api_gateway.get_block_with_biggest_height.assert_called_once
        assert result
        assert result == API_GATEWAY_GET_BLOCK_WITH_BIGGEST_HEIGHT_RESPONSE
