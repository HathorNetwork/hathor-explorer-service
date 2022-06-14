import json

from aws_lambda_context import LambdaContext

from usecases.block_api import BlockApi
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def get_best_chain_height(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    block_api: BlockApi = BlockApi()
) -> dict:
    """Get the best chain height on the ElasticSearch"""

    response = block_api.get_best_chain_height()

    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {
            "Content-Type": "application/json"
        }
    }
