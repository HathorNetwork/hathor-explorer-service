import json
from typing import Union

from aws_lambda_context import LambdaContext

from usecases.list_available_nodes import ListAvailableNodes
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle(
    event: ApiGatewayEvent,
    __: LambdaContext,
    list_available_nodes: Union[ListAvailableNodes, None] = None
) -> dict:

    list_available_nodes = list_available_nodes or ListAvailableNodes()
    response = list_available_nodes.list()

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
