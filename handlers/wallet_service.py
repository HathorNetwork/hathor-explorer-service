import json
from typing import Optional, Union

from aws_lambda_context import LambdaContext

from common.errors import ApiError, RdsNotFoundError
from usecases.wallet_service import WalletService
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle_address_balance(
    event: ApiGatewayEvent,
    __: LambdaContext,
    wallet_service: Union[WalletService, None] = None,
) -> dict:

    wallet_service = wallet_service or WalletService()

    address: Optional[str] = event.query.get("address")
    token: Optional[str] = event.query.get("token")

    if address is None or token is None:
        raise ApiError("invalid_parameters")

    response: Optional[dict]
    try:
        response = wallet_service.address_balance(address, token)
    except RdsNotFoundError:
        raise ApiError("not_found")

    if response is None:
        raise ApiError("not_found")

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def handle_address_history(
    event: ApiGatewayEvent,
    __: LambdaContext,
    wallet_service: Union[WalletService, None] = None,
) -> dict:
    wallet_service = wallet_service or WalletService()

    address: Optional[str] = event.query.get("address")
    token: Optional[str] = event.query.get("token")
    last_tx: str = event.query.get("last_tx", None)
    last_ts_str: str = event.query.get("last_ts", "0")
    limit_str: str = event.query.get("limit", "10")

    if address is None or token is None:
        raise ApiError("invalid_parameters")

    limit: int
    last_ts: int
    try:
        limit = int(limit_str)
        last_ts = int(last_ts_str)
    except ValueError:
        raise ApiError("invalid_parameters")

    if limit > 100:
        raise ApiError("invalid_parameters")

    response = wallet_service.address_history(address, token, limit, last_tx, last_ts)

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"},
    }


@ApiGateway()
def handle_address_tokens(
    event: ApiGatewayEvent,
    __: LambdaContext,
    wallet_service: Union[WalletService, None] = None,
) -> dict:

    wallet_service = wallet_service or WalletService()

    address: Optional[str] = event.query.get("address")
    limit_str: str = event.query.get("limit", "50")
    offset_str: str = event.query.get("offset", "0")

    if address is None:
        raise ApiError("invalid_parameters")

    limit: int
    offset: int
    try:
        limit = int(limit_str)
        offset = int(offset_str)
    except ValueError:
        raise ApiError("invalid_parameters")

    if limit > 100:
        raise ApiError("invalid_parameters")

    response = wallet_service.address_tokens(address, limit, offset)

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"},
    }
