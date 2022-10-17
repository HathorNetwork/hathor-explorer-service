import json
from typing import Union

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.get_token import GetToken
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    get_token: Union[GetToken, None] = None,
) -> dict:

    get_token = get_token or GetToken()
    response = get_token.get(event.path["hash"])

    if response is None:
        raise ApiError("not_found")

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"},
    }
