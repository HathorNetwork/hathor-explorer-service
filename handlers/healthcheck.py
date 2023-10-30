import json
from typing import Optional
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent
from aws_lambda_context import LambdaContext

from usecases.healthcheck import GetHealthcheck

@ApiGateway()
def get_healthcheck(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    healthcheck: Optional[GetHealthcheck] = None,
) -> dict:
    """Get health information about the service and its components."""

    healthcheck = healthcheck or GetHealthcheck()

    response = healthcheck.get_service_health()

    return {
        "statusCode": response.get_http_status_code(),
        "body": json.dumps(response.to_json()),
        "headers": {"Content-Type": "application/json"},
    }