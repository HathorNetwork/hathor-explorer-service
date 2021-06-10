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

    def test_return_500_on_unkown_exception(self):
        function = MagicMock(side_effect=Exception('Boom!'))
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {}
        }

        context = LambdaContext()
        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['statusCode'] == 500
        assert result['body'] == '{"error": "Boom!"}'

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

    def test_returning_cors_headers(self):
        function = MagicMock(return_value={'statusCode': 200, 'headers': {}})
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {}
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers']['Access-Control-Allow-Origin']
        assert result['headers']['Access-Control-Allow-Credentials']

    def test_returning_cors_on_error(self):
        function = MagicMock(return_value={'statusCode': 502, 'headers': {}})
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {}
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers']['Access-Control-Allow-Origin']
        assert result['headers']['Access-Control-Allow-Credentials']
