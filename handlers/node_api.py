import json
from typing import Optional

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.node_api import NodeApi
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent

UNKNOWN_ERROR_MSG = {"error": "unknown_error"}


@ApiGateway()
def get_address_balance(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()
    address = event.query.get("address")
    if address is None:
        raise ApiError("invalid_parameters")

    response = node_api.get_address_balance(address)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
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
        raise ApiError("invalid_parameters")

    if hash is not None and page is None:
        # If hash exists, it"s a paginated request and page is required
        raise ApiError("invalid_parameters")

    response = node_api.get_address_search(address, count, page, hash, token)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def get_version(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()

    response = node_api.get_version()

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def get_dashboard_tx(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()

    block = event.query.get("block")
    tx = event.query.get("tx")

    response = node_api.get_dashboard_tx(block, tx)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def get_transaction_acc_weight(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()
    id = event.query.get("id")
    response = node_api.get_transaction_acc_weight(id)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def get_token_history(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()

    id = event.query.get("id")
    count = event.query.get("count")
    hash = event.query.get("hash")
    page = event.query.get("page")
    timestamp = event.query.get("timestamp")

    if id is None or count is None:
        raise ApiError("invalid_parameters")

    if hash is not None and (page is None or timestamp is None):
        # If hash exists, it"s a paginated request and page is required
        raise ApiError("invalid_parameters")

    response = node_api.get_token_history(id, count, hash, page, timestamp)

    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def get_transaction(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()
    id = event.query.get("id")
    response = node_api.get_transaction(id)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def list_transactions(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()

    type = event.query.get("type")
    count = event.query.get("count")
    hash = event.query.get("hash")
    page = event.query.get("page")
    timestamp = event.query.get("timestamp")

    if type is None or count is None:
        raise ApiError("invalid_parameters")

    if hash is not None and (page is None or timestamp is None):
        # If hash exists, it"s a paginated request and page is required
        raise ApiError("invalid_parameters")

    response = node_api.list_transactions(type, count, hash, page, timestamp)

    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def get_token(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()
    id = event.query.get("id")
    response = node_api.get_token(id)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def list_tokens(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    node_api: Optional[NodeApi] = None
) -> dict:
    node_api = node_api or NodeApi()
    response = node_api.list_tokens()
    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {
            "Content-Type": "application/json"
        }
    }
