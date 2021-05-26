import json

from typing import Callable, Any

from aws_lambda_context import LambdaContext # type: ignore


def parse_body(event: dict):
    try:
        possible_body = event.get('body', '{}')
        return json.loads(possible_body)
    except Exception:
        return dict()


class ApiGatewayEvent:

    def __init__(self, event: dict, context: LambdaContext) -> None:
        self.query = event.get('queryStringParameters', {})
        self.body = parse_body(event)
        self.headers = event.get('headers', {})
        self.request_id = context.aws_request_id


class ApiGateway:

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __call__(self, function_to_call: Callable[[ApiGatewayEvent, LambdaContext, Any, Any], dict]) -> Callable[[dict, LambdaContext, Any, Any], dict]:
        def wrapper(event: dict, context: LambdaContext, *args: Any, **kwargs: Any) -> dict:
            errors_status = {
                'invalid_parameters': 400,
                'not_authorized': 401,
                'internal_error': 500,
                'not_found': 404
            }

            try:
                api_gateway_event = ApiGatewayEvent(event, context)
                result = function_to_call(api_gateway_event, context, *args, **kwargs) # type: ignore
                return result
            except Exception as error:
                return {
                    'statusCode': errors_status[str(error)],
                    'body': json.dumps({
                        'error': str(error)
                    })
                }

        return wrapper
