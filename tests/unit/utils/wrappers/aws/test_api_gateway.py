import pytest

from unittest.mock import MagicMock
from aws_lambda_context import LambdaContext

from utils.wrappers.aws.api_gateway import ApiGateway


class TestApiGateway:

    def test_calling_function(self):
        function = MagicMock(return_value={'statusCode': 200, 'headers': {}})
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {}
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['statusCode'] == 200

    def test_returning_error(self):
        function = MagicMock(side_effect=Exception('not_authorized'))
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {}
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['statusCode'] == 401

    def test_raising_exception(self):
        function = MagicMock(side_effect=Exception('Boom!'))
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {}
        }

        context = LambdaContext()

        with pytest.raises(Exception, match=r"Boom"):
            api_gateway.__call__(function)(event, context)

    def test_parse_json_fail_proof(self):
        function = MagicMock(return_value={'statusCode': 200, 'headers': {}})
        api_gateway = ApiGateway()

        event = {
            'body': 'bad-json-value',
            'headers': {}
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['statusCode'] == 200
