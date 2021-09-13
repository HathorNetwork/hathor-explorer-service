import json
from typing import Union

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.get_node import GetNode
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle(event: ApiGatewayEvent, __: LambdaContext, get_node: Union[GetNode, None] = None) -> dict:

    get_node = get_node or GetNode()
    response = get_node.get(event.path['hash'])

    if response is None:
        raise ApiError('not_found')

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
