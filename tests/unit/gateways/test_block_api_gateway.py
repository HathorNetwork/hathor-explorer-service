from unittest.mock import MagicMock

from tests.fixtures.elastic_search_fixtures import (
    ELASTIC_SEARCH_BEST_CHAIN_HEIGHT_SUCCESSFUL_RAW_RESPONSE,
    GATEWAY_BEST_CHAIN_HEIGHT_SUCCESSFUL_RESPONSE,
)
from pytest import fixture

from gateways.block_api_gateway import BlockApiGateway

from elasticsearch import TransportError


class TestBlockApiGateway:
    @fixture
    def elastic_search_client(self):
        return MagicMock()

    def test_get_best_chain_height(self, elastic_search_client):
        """ Test if ElasticSearch client is being called
            and if the response is being treated before returning the data
        """
        elastic_search_client.search = MagicMock(
            return_value=ELASTIC_SEARCH_BEST_CHAIN_HEIGHT_SUCCESSFUL_RAW_RESPONSE
        )

        gateway = BlockApiGateway(elastic_search_client=elastic_search_client)
        result = gateway.get_best_chain_height()

        elastic_search_client.search.assert_called_once()
        assert result == GATEWAY_BEST_CHAIN_HEIGHT_SUCCESSFUL_RESPONSE

    def test_get_best_chain_height_with_exception(self, elastic_search_client):
        """ Test if dict with the status code and error message is returned when call to elasticsearch fails
        """

        elastic_search_client.search.side_effect = TransportError('Boom')
        gateway = BlockApiGateway(elastic_search_client=elastic_search_client)
        result = gateway.get_best_chain_height()
        assert 'error' in result
        assert result['status'] == 500
