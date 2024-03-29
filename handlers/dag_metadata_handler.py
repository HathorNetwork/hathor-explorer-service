from typing import Optional

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.metadata import Metadata
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent
from utils.wrappers.aws.invoke_handler import (
    InvokeEvent,
    InvokeHandler,
    MetadataUpdateEvent,
)


@ApiGateway()
def handle_get(
    event: ApiGatewayEvent, _context: LambdaContext, metadata: Optional[Metadata] = None
) -> dict:
    metadata = metadata or Metadata()
    if "id" not in event.query:
        raise ApiError("invalid_parameters")
    hash = event.query["id"]
    response = metadata.get("dag", hash)

    if response is None:
        raise ApiError("not_found")

    return {
        "statusCode": 200,
        "body": response,
        "headers": {"Content-Type": "application/json"},
    }


@InvokeHandler()
def handle_create_or_update(
    event: InvokeEvent, _context: LambdaContext, metadata: Optional[Metadata] = None
) -> dict:
    metadata = metadata or Metadata()

    parsed_event = MetadataUpdateEvent.from_event(event)

    tx_id = parsed_event.id
    tx_metadata = parsed_event.metadata

    metadata.create_or_update_dag(tx_id, tx_metadata)

    return dict(success=True, id=tx_id)
