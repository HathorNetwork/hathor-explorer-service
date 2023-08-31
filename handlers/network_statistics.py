import json
from typing import Optional

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.network_statistics_api import NetworkStatisticsApi
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def get_basic_statistics(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    network_statistics_api: Optional[NetworkStatisticsApi] = None,
) -> dict:
    """Get token balances from user search"""

    network_statistics_api = network_statistics_api or NetworkStatisticsApi()

    response = network_statistics_api.get_basic_statistics()

    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {
        },
    }
