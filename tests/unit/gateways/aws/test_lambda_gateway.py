from unittest.mock import MagicMock, patch

import pytest

from tests.fixtures.node_factory import NodeFactory
from gateways.aws.lambda_gateway import LambdaGateway
from pytest import fixture


class TestLambdaGateway:

    @fixture
    def lambda_client(self):
        return MagicMock()

    @patch('gateways.aws.lambda_gateway.DATA_AGGREGATOR_LAMBDA_NAME', 'data-aggregator')
    def test_node_to_data_aggregator(self, lambda_client):
        lambda_client.invoke_async = MagicMock(return_value=202)

        gateway = LambdaGateway(lambda_client)

        node_data = NodeFactory()
        result = gateway.send_node_to_data_aggregator(node_data)

        lambda_client.invoke_async.assert_called_once_with('data-aggregator', node_data.to_dict())
        assert result == 202

    @patch('gateways.aws.lambda_gateway.DATA_AGGREGATOR_LAMBDA_NAME', None)
    def test_node_to_data_aggregator_error(self, lambda_client):
        gateway = LambdaGateway(lambda_client)
        node_data = NodeFactory()

        with pytest.raises(Exception, match=r'No lambda name in config'):
            gateway.send_node_to_data_aggregator(node_data)
