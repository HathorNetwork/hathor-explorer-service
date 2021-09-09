from typing import Union

from aws_lambda_context import LambdaContext

from usecases.get_metadata import GetMetadata
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    get_metadata: Union[GetMetadata, None] = None
) -> dict:

    get_metadata = get_metadata or GetMetadata()
    hash = event.query['id']
    response = get_metadata.get('dag', hash)

    if response is None:
        raise Exception('not_found')

    return {
        "statusCode": 200,
        "body": response,
        "headers": {
            "Content-Type": "application/json"
        }
    }
