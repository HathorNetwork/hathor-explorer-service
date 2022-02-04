from unittest.mock import MagicMock, patch

from aws_lambda_context import LambdaContext

from common.errors import ApiError
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
        function = MagicMock(side_effect=ApiError('not_authorized'))
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {}
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['statusCode'] == 401

    def test_return_500_on_unkown_apierror(self):
        function = MagicMock(side_effect=ApiError('Boom!'))
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

    @patch('utils.wrappers.aws.api_gateway.CORS_ALLOWED_REGEX', 'https?://([a-z0-9])*[.]*hathor[.]network')
    def test_returning_cors_headers(self):
        function = MagicMock(return_value={'statusCode': 200, 'headers': {}})
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {
                'origin': 'https://explorer.hathor.network'
            }
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers']['Access-Control-Allow-Origin']
        assert result['headers']['Access-Control-Allow-Credentials']

    @patch('utils.wrappers.aws.api_gateway.CORS_ALLOWED_REGEX', 'https?://([a-z0-9]+[.])*hathor[.]network')
    def test_returning_cors_headers_testnet(self):
        function = MagicMock(return_value={'statusCode': 200, 'headers': {}})
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {
                'origin': 'https://explorer.testnet.hathor.network'
            }
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers']['Access-Control-Allow-Origin']
        assert result['headers']['Access-Control-Allow-Credentials']

    @patch('utils.wrappers.aws.api_gateway.CORS_ALLOWED_REGEX', 'https?://([a-z0-9]+[.])*hathor[.]network')
    def test_returning_cors_headers_golf(self):
        function = MagicMock(return_value={'statusCode': 200, 'headers': {}})
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {
                'origin': 'https://explorer.golf.hathor.network'
            }
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers']['Access-Control-Allow-Origin']
        assert result['headers']['Access-Control-Allow-Credentials']

    @patch('utils.wrappers.aws.api_gateway.CORS_ALLOWED_REGEX', 'https?://([a-z0-9])*[.]*hathor[.]network')
    def test_cors_fail_regex_not_matching(self):
        function = MagicMock(return_value={'statusCode': 200, 'headers': {}})
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {
                'origin': 'https://explorer.anydomain.network'
            }
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers'] == {}

    @patch('utils.wrappers.aws.api_gateway.CORS_ALLOWED_REGEX', 'https?://([a-z0-9])*[.]*hathor[.]network')
    def test_returning_cors_on_apierror(self):
        function = MagicMock(side_effect=ApiError('Boom!'))
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {
                'origin': 'https://explorer.hathor.network'
            }
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers']['Access-Control-Allow-Origin']
        assert result['headers']['Access-Control-Allow-Credentials']

    @patch('utils.wrappers.aws.api_gateway.CORS_ALLOWED_REGEX', 'https?://([a-z0-9])*[.]*hathor[.]network')
    def test_returning_cors_on_error(self):
        function = MagicMock(side_effect=Exception('Boom!'))
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {
                'origin': 'https://explorer.hathor.network'
            }
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers']['Access-Control-Allow-Origin']
        assert result['headers']['Access-Control-Allow-Credentials']

    @patch('utils.wrappers.aws.api_gateway.CORS_ALLOWED_REGEX', 'https?://([a-z0-9])*[.]*hathor[.]network')
    def test_works_with_no_headers_from_function(self):
        function = MagicMock(return_value={'statusCode': 200})
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {
                'origin': 'https://explorer.hathor.network'
            }
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers']

    @patch('utils.wrappers.aws.api_gateway.CORS_ALLOWED_REGEX', None)
    def test_no_headers_with_no_config(self):
        function = MagicMock(return_value={'statusCode': 200})
        api_gateway = ApiGateway()

        event = {
            'body': '{}',
            'headers': {}
        }

        context = LambdaContext()

        result = api_gateway.__call__(function)(event, context)

        function.assert_called()
        assert result['headers'] == {}
