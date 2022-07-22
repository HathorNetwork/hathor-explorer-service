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
    wallet_service: Union[WalletService, None] = None
) -> dict:

    wallet_service = wallet_service or WalletService()

    address = event.query.get("address")
    token = event.query.get("token")

    if address is None or token is None:
        raise ApiError("invalid_parameters")

    response: Optional[dict]
    try:
        response = wallet_service.address_balance(address, token)
    except RdsNotFoundError:
        raise ApiError('not_found')

    if response is None:
        raise ApiError('not_found')

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def handle_address_history(
    event: ApiGatewayEvent,
    __: LambdaContext,
    wallet_service: Union[WalletService, None] = None
) -> dict:

    wallet_service = wallet_service or WalletService()

    address = event.query.get("address")
    token = event.query.get("token")
    limit_str = event.query.get("limit", 10)
    skip_str = event.query.get("skip", 0)

    if address is None or token is None:
        raise ApiError("invalid_parameters")

    limit: int
    skip: int
    try:
        limit = int(limit_str)
        skip = int(skip_str)
    except ValueError:
        raise ApiError("invalid_parameters")

    response = wallet_service.address_history(address, token, int(limit), int(skip))

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }


@ApiGateway()
def handle_address_tokens(
    event: ApiGatewayEvent,
    __: LambdaContext,
    wallet_service: Union[WalletService, None] = None
) -> dict:

    wallet_service = wallet_service or WalletService()

    address = event.query.get("address")

    if address is None:
        raise ApiError("invalid_parameters")

    response = wallet_service.address_tokens(address)

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
