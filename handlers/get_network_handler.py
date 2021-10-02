import json
from typing import Optional

from aws_lambda_context import LambdaContext

from usecases.get_network import GetNetwork
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle(event: ApiGatewayEvent, __: LambdaContext, get_network: Optional[GetNetwork] = None) -> dict:

    get_network = get_network or GetNetwork()
    response = get_network.get()

    if response is None:
        raise Exception('not_found')

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
