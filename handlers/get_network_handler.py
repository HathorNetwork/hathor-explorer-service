import json
from typing import Union

from aws_lambda_context import LambdaContext

from usecases.get_network import GetNetwork
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle(event: ApiGatewayEvent, __: LambdaContext, get_network: Union[GetNetwork, None] = None) -> dict:

    get_network = get_network or GetNetwork()
    response = get_network.get(event.path['hash'])

    if response is None:
        raise Exception('not_found')

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
