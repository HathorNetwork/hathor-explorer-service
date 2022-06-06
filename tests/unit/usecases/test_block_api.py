from unittest.mock import MagicMock

from pytest import fixture

from usecases.block_api import BlockApi


class TestBlockApi:

    @fixture
    def block_api_gateway(self):
        return MagicMock()

    @fixture
    def api_gateway_get_block_with_biggest_height_response(self):
        return {
            'hits':
            [
                {
                    'tx_id': '00a1786694f2b2248c4272e64f9f414759322b4e6d5e40d39cc5b5aedfd70dfb',
                    'timestamp': '2022-05-09T18:55:47Z',
                    'version': 0,
                    'voided': False,
                    'height': 1740645,
                    'weight': 60.66999816894531
                }
            ],
            'has_next': False
        }

    def test_get_block_with_biggest_height(
        self,
        block_api_gateway,
        api_gateway_get_block_with_biggest_height_response
    ):
        api_gateway_response = api_gateway_get_block_with_biggest_height_response
        block_api_gateway.get_block_with_biggest_height = MagicMock(return_value=api_gateway_response)

        block_api = BlockApi(block_api_gateway)

        result = block_api.get_block_with_biggest_height()
        block_api_gateway.get_block_with_biggest_height.assert_called_once
        assert result
        assert result == api_gateway_response
