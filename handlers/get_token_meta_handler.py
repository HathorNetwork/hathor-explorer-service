import json
from typing import Union
from usecases.get_token_metadata import GetTokenMetadata

from aws_lambda_context import LambdaContext
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def handle(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    get_token_metadata: Union[GetTokenMetadata, None] = None
) -> dict:

    get_token_metadata = get_token_metadata or GetTokenMetadata()
    response = get_token_metadata.get(event.path['hash'])

    if response is None:
        raise Exception('not_found')

    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json"
        }
    }
