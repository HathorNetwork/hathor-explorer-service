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
    address = event.query.get("address")
    if address is None:
        raise Exception("invalid_parameters")

    response = node_api.get_address_balance(address)
    if response is None:
        return {
            "statusCode": 503,
            "body": json.dumps({"error": "unknown_error"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def get_address_search(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()

    address = event.query.get("address")
    count = event.query.get("count")
    page = event.query.get("page")
    hash = event.query.get("hash")
    token = event.query.get("token")
    if address is None or count is None:
        raise Exception("invalid_parameters")

    if hash is not None and page is None:
        # If hash exists, it"s a paginated request and page is required
        raise Exception("invalid_parameters")

    response = node_api.get_address_search(address, count, page, hash, token)

    if response is None:
        return {
            "statusCode": 503,
            "body": json.dumps({"error": "unknown_error"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
