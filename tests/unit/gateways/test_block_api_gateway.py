from unittest.mock import MagicMock

from pytest import fixture

from gateways.block_api_gateway import BlockApiGateway
from tests.fixtures.elastic_search_fixtures import (
    ELASTIC_SEARCH_BEST_CHAIN_HEIGHT_SUCCESSFUL_RAW_RESPONSE,
    GATEWAY_BEST_CHAIN_HEIGHT_SUCCESSFUL_RESPONSE,
)


class TestBlockApiGateway:
    @fixture
    def elastic_search_client(self):
        return MagicMock()

    def test_get_best_chain_height(self, elastic_search_client):
        """Test if ElasticSearch client is being called
        and if the response is being treated before returning the data
        """
        elastic_search_client.search = MagicMock(
            return_value=ELASTIC_SEARCH_BEST_CHAIN_HEIGHT_SUCCESSFUL_RAW_RESPONSE
        )

        gateway = BlockApiGateway(elastic_search_client=elastic_search_client)
        result = gateway.get_best_chain_height()

        elastic_search_client.search.assert_called_once()
        assert result == GATEWAY_BEST_CHAIN_HEIGHT_SUCCESSFUL_RESPONSE
