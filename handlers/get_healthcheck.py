import json
from typing import Optional

from aws_lambda_context import LambdaContext

from usecases.get_healthcheck import GetHealthcheck
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def get_healthcheck(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    healthcheck: Optional[GetHealthcheck] = None,
) -> dict:
    """Get health information about the service and its components."""

    healthcheck = healthcheck or GetHealthcheck()

    response, status_code = healthcheck.get_service_health()

    return {
        "statusCode": status_code,
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"},
    }
