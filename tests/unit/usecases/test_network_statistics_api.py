import types
from unittest.mock import Mock

import pytest
from elasticsearch import exceptions
from pytest import fixture

from common.errors import ApiError
from tests.fixtures.elastic_search_fixtures import (
    NETWORK_STATISTICS_SUCCESSFUL_RESPONSE,
)
from usecases.network_statistics_api import NetworkStatisticsApi


class TestNetworkStatisticsApi:
    @fixture
    def network_statistics_api_gateway(self):
        return Mock()

    def test_get_basic_statistics(self, network_statistics_api_gateway):
        fake_api_response = NETWORK_STATISTICS_SUCCESSFUL_RESPONSE
        network_statistics_api_gateway.get_transaction_statistics = Mock(
            return_value=fake_api_response
        )

        network_statistics_api = NetworkStatisticsApi(network_statistics_api_gateway)
        result = network_statistics_api.get_basic_statistics()

        assert result
        assert result == fake_api_response

    def test_get_basic_statistics_api_error(self, network_statistics_api_gateway):
        error_meta = types.SimpleNamespace(
            status=500, http_version="1.1", headers={}, duration=0.0, node=None
        )
        error = exceptions.ApiError(
            message="InternalServerError", meta=error_meta, body={}
        )
        mock = Mock(side_effect=error)
        network_statistics_api_gateway.get_transaction_statistics = mock

        network_statistics_api = NetworkStatisticsApi(network_statistics_api_gateway)
        with pytest.raises(ApiError, match="gateway_error"):
            network_statistics_api.get_basic_statistics()

    def test_get_basic_statistics_transport_error(self, network_statistics_api_gateway):
        error = exceptions.TransportError(
            message="InternalServerError",
        )
        mock = Mock(side_effect=error)
        network_statistics_api_gateway.get_transaction_statistics = mock

        network_statistics_api = NetworkStatisticsApi(network_statistics_api_gateway)
        with pytest.raises(ApiError, match="internal_error"):
            network_statistics_api.get_basic_statistics()
