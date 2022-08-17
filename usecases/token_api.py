from typing import List, Optional

from gateways.token_api_gateway import TokenApiGateway


class TokenApi:
    def __init__(self, token_api_gateway: Optional[TokenApiGateway] = None) -> Optional[None]:
        self.token_api_gateway = token_api_gateway or TokenApiGateway()

    def get_tokens(self, search_text: str, sort_by: str, order: str, search_after: List[str]) -> dict:
        return self.token_api_gateway.get_tokens(search_text, sort_by, order, search_after)

    def get_token(self, token_id: str) -> dict:
        return self.token_api_gateway.get_token(token_id)
