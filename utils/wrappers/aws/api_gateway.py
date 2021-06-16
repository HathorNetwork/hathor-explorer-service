import json
from typing import Any, Callable

from aws_lambda_context import LambdaContext


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

            try:
                api_gateway_event = ApiGatewayEvent(event, context)
                result = function_to_call(api_gateway_event, context, *args, **kwargs)  # type: ignore

                result['headers']['Access-Control-Allow-Origin'] = '*'
                result['headers']['Access-Control-Allow-Credentials'] = True

                return result
            except Exception as error:
                error_key = str(error)

                if error_key not in errors_status.keys():
                    error_key = 'internal_error'

                return {
                    'statusCode': errors_status[error_key],
                    'body': json.dumps({
                        'error': str(error)
                    })
                }

        return wrapper
