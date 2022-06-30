from typing import Optional

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.put_metadata import PutMetadata
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    put_metadata: Optional[PutMetadata] = None
) -> dict:

    put_metadata = put_metadata or PutMetadata()
    if 'id' not in event.query:
        raise ApiError('invalid_parameters')
    hash = event.query['id']
    response = put_metadata.get('dag', hash)

    if response is None:
        raise ApiError('not_found')

    return {
        "statusCode": 200,
        "body": response,
        "headers": {
            "Content-Type": "application/json"
        }
    }
