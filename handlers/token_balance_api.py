import json
from typing import Optional

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.token_balances_api import TokenBalancesApi
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def get_token_balances(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    token_balances_api: Optional[TokenBalancesApi] = None
) -> dict:
    """Get token balances from user search"""

    token_balances_api = token_balances_api or TokenBalancesApi()

    token_id = event.query.get('token_id') or "00"
    sort_by = event.query.get('sort_by') or ""
    order = event.query.get('order') or 'asc'  # asc/desc
    search_after = event.query.get('search_after') or ''
    search_after_list = []

    if search_after:
        search_after_list = list(search_after.split(","))

        if len(search_after_list) != 2:
            raise ApiError('Invalid search_after parameter')

    response = token_balances_api.get_token_balances(token_id, sort_by, order, search_after_list)

    return {
        'statusCode': 200,
        'body': json.dumps(response or {}),
        'headers': {
            'Content-Type': 'application/json'
        }
    }


@ApiGateway()
def get_token_information(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    token_balances_api: TokenBalancesApi = TokenBalancesApi()
) -> dict:
    """Get token information from a given token_id
    """

    token_id = event.query.get('token_id') or '00'
    response = token_balances_api.get_token_information(token_id)

    return {
        'statusCode': 200,
        'body': json.dumps(response or {}),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
