from unittest.mock import MagicMock

from pytest import fixture

from gateways.network_statistics_api_gateway import NetworkStatisticsApiGateway
from tests.fixtures.elastic_search_fixtures import (
    NETWORK_STATISTICS_RAW_RESPONSE,
    NETWORK_STATISTICS_SUCCESSFUL_RESPONSE,
)


class TestNetworkStatisticsApiGateway:
    @fixture
    def elastic_search_client(self):
        return MagicMock()

    def test_get_transaction_statistics(self, elastic_search_client):
        """Test if ElasticSearch client is being called
        and if the response is being treated before returning the data
        """
        elastic_search_client.search = MagicMock(
            return_value=NETWORK_STATISTICS_RAW_RESPONSE
        )

        gateway = NetworkStatisticsApiGateway(
            elastic_search_client=elastic_search_client
        )
        result = gateway.get_transaction_statistics()

        elastic_search_client.search.assert_called_once()
        assert result == NETWORK_STATISTICS_SUCCESSFUL_RESPONSE
