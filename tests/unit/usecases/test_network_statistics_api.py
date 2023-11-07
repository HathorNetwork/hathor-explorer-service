from unittest.mock import MagicMock, patch

from elasticsearch import exceptions
from pytest import fixture, raises

from common.errors import ApiError
from usecases.network_statistics_api import NetworkStatisticsApi


class TestNetworkStatisticsApi:
    @fixture
    def gateway(self):
        return MagicMock()

    @patch("usecases.network_statistics_api.logger")
    def test_get_basic_statistics(self, logger, gateway):
        api = NetworkStatisticsApi(network_statistics_api_gateway=gateway)
        gateway.get_transaction_statistics.return_value = {"foo": "bar"}
        result = api.get_basic_statistics()
        gateway.get_transaction_statistics.assert_called_once()
        assert result == {"foo": "bar"}

    @patch("usecases.network_statistics_api.logger")
    def test_get_basic_statistics_gateway_error(self, logger, gateway):
        api = NetworkStatisticsApi(network_statistics_api_gateway=gateway)
        gateway.get_transaction_statistics.side_effect = exceptions.ApiError(
            "gateway_error", MagicMock(), MagicMock()
        )
        with raises(ApiError):
            api.get_basic_statistics()
        gateway.get_transaction_statistics.assert_called_once()
        logger.error.assert_called_once()

    @patch("usecases.network_statistics_api.logger")
    def test_get_basic_statistics_internal_error(self, logger, gateway):
        api = NetworkStatisticsApi(network_statistics_api_gateway=gateway)
        gateway.get_transaction_statistics.side_effect = exceptions.TransportError(
            "internal_error"
        )
        with raises(ApiError):
            api.get_basic_statistics()
        gateway.get_transaction_statistics.assert_called_once()
        logger.error.assert_called_once()
