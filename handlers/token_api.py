import json
from typing import Optional

from aws_lambda_context import LambdaContext

from common.errors import ApiError
from usecases.token_api import TokenApi
from utils.wrappers.aws.api_gateway import ApiGateway, ApiGatewayEvent


@ApiGateway()
def get_tokens(
    event: ApiGatewayEvent,
    _context: LambdaContext,
    token_api: Optional[TokenApi] = None
) -> dict:
    """Get tokens from user search"""

    token_api = token_api or TokenApi()

    search_text = event.query.get("search_text") or ""
    sort_by = event.query.get("sort_by") or ""
    order = event.query.get("order") or "asc"  # asc/desc
    search_after = event.query.get("search_after") or ""
    search_after_list = []

    if sort_by == "uid":
        sort_by = "id"

    if search_after:
        search_after_list = list(search_after.split(","))

        if len(search_after_list) != 2:
            raise ApiError("Invalid search_after parameter")

    response = token_api.get_tokens(search_text, sort_by, order, search_after_list)

    return {
        "statusCode": 200,
        "body": json.dumps(response or {}),
        "headers": {
            "Content-Type": "application/json"
        }
    }