from unittest.mock import MagicMock

from gateways.network_statistics_api_gateway import NetworkStatisticsApiGateway


class TestNetworkStatisticsApiGateway:
    def setup_method(self):
        self.mock_elastic_search_client = MagicMock()
        self.network_statistics_api_gateway = NetworkStatisticsApiGateway(
            self.mock_elastic_search_client
        )

    def test_init(self):
        assert (
            self.network_statistics_api_gateway.elastic_search_client
            == self.mock_elastic_search_client
        )

    def test_get_transaction_statistics(self):
        mock_response = {
            "aggregations": {
                "total_transactions": {"value": 100},
                "total_custom_tokens": {"value": 50},
                "highest_height": {"value": 1000},
            }
        }
        self.mock_elastic_search_client.run.return_value = mock_response

        result = self.network_statistics_api_gateway.get_transaction_statistics()

        assert result == {
            "total_transactions": 100,
            "total_custom_tokens": 50,
            "highest_height": 1000,
        }
        self.mock_elastic_search_client.run.assert_called_once()
