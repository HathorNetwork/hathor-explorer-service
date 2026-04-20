import base64
from typing import Optional

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.metadata import Metadata
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle_get(
    event: ApiGatewayEvent, _context: LambdaContext, metadata: Optional[Metadata] = None
) -> dict:
    metadata = metadata or Metadata()
    if "id" not in event.query:
        raise ApiError("invalid_parameters")
    icon_id = event.query["id"]
    response = metadata.get("icon", icon_id)

    if response is None:
        raise ApiError("not_found")
    if not isinstance(response, bytes):
        raise ApiError("internal_error")

    return {
        "statusCode": 200,
        "body": base64.b64encode(response).decode(),
        "isBase64Encoded": True,
        "headers": {"Content-Type": "image/png"},
    }
