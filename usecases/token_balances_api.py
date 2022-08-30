from typing import List, Optional

from gateways.token_balances_api_gateway import TokenBalancesApiGateway


class TokenBalancesApi:
    def __init__(
        self, token_balances_api_gateway: Optional[TokenBalancesApiGateway] = None
    ) -> Optional[None]:
        self.token_balances_api_gateway = (
            token_balances_api_gateway or TokenBalancesApiGateway()
        )

    def get_token_balances(
        self, token_id: str, sort_by: str, order: str, search_after: List[str]
    ) -> dict:
        return self.token_balances_api_gateway.get_token_balances(
            token_id, sort_by, order, search_after
        )

    def get_token_information(self, token_id: str) -> dict:
        return self.token_balances_api_gateway.get_token_information(token_id)
