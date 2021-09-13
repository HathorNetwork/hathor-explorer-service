import json
from typing import Any, Callable

from aws_lambda_context import LambdaContext

from common.configuration import CORS_ALLOWED_ORIGIN
from common.errors import ApiError


def parse_body(event: dict) -> dict:
    try:
        possible_body = event.get('body', '{}')
        return json.loads(possible_body)
    except Exception:
        return dict()


class ApiGatewayEvent:

    def __init__(self, event: dict, context: LambdaContext) -> None:
        self.query = event.get('queryStringParameters', {})
        self.path = event.get('pathParameters', {})
        self.body = parse_body(event)
        self.headers = event.get('headers', {})


class ApiGateway:

    def __call__(
        self,
        function_to_call: Callable[[ApiGatewayEvent, LambdaContext, Any], dict]
    ) -> Callable[[dict, LambdaContext, Any], dict]:
        def wrapper(event: dict, context: LambdaContext, *args: Any, **kwargs: Any) -> dict:
            errors_status = {
                'invalid_parameters': 400,
                'not_authorized': 401,
                'internal_error': 500,
                'not_found': 404
            }

            headers = {}

            if CORS_ALLOWED_ORIGIN:
                headers = {
                    'Access-Control-Allow-Origin': CORS_ALLOWED_ORIGIN,
                    'Access-Control-Allow-Credentials': True
                }

            try:
                api_gateway_event = ApiGatewayEvent(event, context)
                result = function_to_call(api_gateway_event, context, *args, **kwargs)  # type: ignore

                if result.get('headers') is None:
                    result['headers'] = {}

                result['headers'].update(headers)

                return result
            except ApiError as error:
                error_key = str(error)

                if error_key not in errors_status.keys():
                    error_key = 'internal_error'

                return {
                    'headers': headers,
                    'statusCode': errors_status[error_key],
                    'body': json.dumps({
                        'error': str(error)
                    })
                }
            except Exception as error:
                return {
                    'headers': headers,
                    'statusCode': 500,
                    'body': json.dumps({
                        'error': str(error)
                    })
                }

        return wrapper
