import json
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
    type = event.path['type']
    hash = event.path['hash']
    response = get_metadata.get(type, hash)

    if response is None:
        raise Exception('not_found')

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
