import os

from unittest.mock import MagicMock, patch

import pytest

from tests.fixtures.network_factory import NetworkFactory
from gateways.aws.lambda_gateway import LambdaGateway
from pytest import fixture


class TestLambdaGateway:

    @fixture
    def lambda_client(self):
        return MagicMock()

    @patch.dict(os.environ, {"DATA_AGGREGATOR_LAMBDA_NAME": "data-aggregator"})
    def test_network_to_data_aggregator(self, lambda_client):
        lambda_client.invoke_async = MagicMock(return_value=202)

        gateway = LambdaGateway(lambda_client)

        network_data = NetworkFactory()
        result = gateway.send_network_to_data_aggregator(network_data)

        lambda_client.invoke_async.assert_called_once_with('data-aggregator', network_data.to_dict())
        assert result == 202

    def test_network_to_data_aggregator_error(self, lambda_client):
        gateway = LambdaGateway()
        network_data = NetworkFactory()

        with pytest.raises(Exception, match=r'No lambda name in config'):
            gateway.send_network_to_data_aggregator(network_data)
