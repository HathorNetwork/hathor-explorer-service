import json
from typing import Optional

from aws_lambda_context import LambdaContext

from usecases.block_api import BlockApi
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def get_block_with_biggest_height(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    block_api: Optional[BlockApi] = None
) -> dict:
    """Get the block with biggest height available on the ElasticSearch"""

    block_api = block_api or BlockApi()
    response = block_api.get_block_with_biggest_height()

    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {
            "Content-Type": "application/json"
        }
    }
