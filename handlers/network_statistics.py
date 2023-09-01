import json
from typing import Optional

from aws_lambda_context import LambdaContext

from usecases.network_statistics_api import NetworkStatisticsApi
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def get_basic_statistics(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    network_statistics_api: Optional[NetworkStatisticsApi] = None,
) -> dict:
    """Get basic network statistics such as total transactions,
    total custom tokens and highest height from the best blockchain."""

    network_statistics_api = network_statistics_api or NetworkStatisticsApi()

    response = network_statistics_api.get_basic_statistics()

    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {"Content-Type": "application/json"},
    }
