import json
from typing import Optional

from aws_lambda_context import LambdaContext

from usecases.node_api import NodeApi
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def get_address_balance(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()
    address = event.query.get('address')
    if address is None:
        raise Exception('invalid_parameters')

    response = node_api.get_address_balance(address)

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
