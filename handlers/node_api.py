import json
from typing import Optional

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.node_api import NodeApi
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent

UNKNOWN_ERROR_MSG = {"error": "unknown_error"}


@ApiGateway()
def get_address_balance(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get the token balance of a given address.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
    node_api = node_api or NodeApi()
    address = event.query.get("address")
    if address is None:
        raise ApiError("invalid_parameters")

    response = node_api.get_address_balance(address)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def get_address_search(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get a paginated list of transactions for a given address.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
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
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def get_version(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get the node version settings.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
    node_api = node_api or NodeApi()

    response = node_api.get_version()

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def get_dashboard_tx(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get the txs and blocks to be shown on the dashboard.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
    node_api = node_api or NodeApi()

    block = event.query.get("block")
    tx = event.query.get("tx")

    if block is None or tx is None:
        raise ApiError("invalid_parameters")

    response = node_api.get_dashboard_tx(block, tx)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def get_transaction_acc_weight(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get a tx accumulated weight data.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
    node_api = node_api or NodeApi()
    id = event.query.get("id")

    if id is None:
        raise ApiError("invalid_parameters")

    response = node_api.get_transaction_acc_weight(id)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def get_token_history(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get a paginated history of transactions for a given token id.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
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
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def get_transaction(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get transaction details given a tx_id.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
    node_api = node_api or NodeApi()
    id = event.query.get("id")

    if id is None:
        raise ApiError("invalid_parameters")
    response = node_api.get_transaction(id)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def get_feature(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get feature activation details.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
    node_api = node_api or NodeApi()
    block = event.query.get("block")
    response = node_api.get_feature(block)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def list_transactions(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get a pagination on blocks or transactions with details.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
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
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def get_token(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get token details given a token uid.

    *IMPORTANT: Any changes on the parameters should be reflected on the `cacheKeyParameters` for this method.
    """
    node_api = node_api or NodeApi()
    id = event.query.get("id")

    if id is None:
        raise ApiError("invalid_parameters")
    response = node_api.get_token(id)

    return {
        "statusCode": 200,
        "body": json.dumps(response or UNKNOWN_ERROR_MSG),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def decode_tx(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Decode a tx by it's struct data hex encoded."""
    node_api = node_api or NodeApi()
    hex_tx = event.query.get("hex_tx")

    if hex_tx is None:
        raise ApiError("invalid_parameters")
    response = node_api.decode_tx(hex_tx)
    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def push_tx(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Push a transaction by it's struct data hex encoded."""
    node_api = node_api or NodeApi()
    hex_tx = event.body.get("hex_tx")

    if hex_tx is None:
        raise ApiError("invalid_parameters")
    response = node_api.push_tx(hex_tx)
    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def graphviz_dot_neighbors(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Generate file with the graph of neighbours of a tx in dot format."""
    node_api = node_api or NodeApi()
    tx = event.query.get("tx")
    graph_type = event.query.get("graph_type")  # verification, funds
    max_level = event.query.get("max_level")

    if tx is None or graph_type is None or max_level is None:
        raise ApiError("invalid_parameters")
    response = node_api.graphviz_dot_neighbors(tx, graph_type, max_level)
    return {
        "statusCode": 200,
        "body": response,
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def nc_state(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get state of a nano contract."""
    node_api = node_api or NodeApi()
    id = event.query.get("id")
    fields = event.multiValueQueryStringParameters.get("fields[]")
    balances = event.multiValueQueryStringParameters.get("balances[]")
    calls = event.multiValueQueryStringParameters.get("calls[]")

    response = node_api.get_nc_state(id, fields, balances, calls)
    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def nc_history(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get history of a nano contract."""
    node_api = node_api or NodeApi()
    id = event.query.get("id")

    response = node_api.get_nc_history(id)
    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {"Content-Type": "application/json"},
    }

@ApiGateway()
def nc_blueprint_information(
    event: ApiGatewayEvent, _context: LambdaContext, node_api: Optional[NodeApi] = None
) -> dict:
    """Get blueprint information."""
    node_api = node_api or NodeApi()
    blueprint_id = event.query.get("blueprint_id")

    response = node_api.get_nc_blueprint_information(blueprint_id)
    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {"Content-Type": "application/json"},
    }
