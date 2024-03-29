from typing import Optional

from domain.tx.token import Token
from gateways.clients.hathor_core_client import TOKEN_ENDPOINT, HathorCoreClient
from gateways.clients.responses.hathor_core.hathor_core_token_response import (
    HathorCoreTokenResponse,
)


class TokenGateway:
    """Gateway for Token

    :param hathor_core_client: Client for make hathor-core requests, default to domain HathorCoreClient
    :type hathor_core_client:
    """

    def __init__(self, hathor_core_client: Optional[HathorCoreClient] = None) -> None:
        self.hathor_core_client = hathor_core_client or HathorCoreClient()

    def get_token(self, id: str) -> Optional[Token]:
        """Retrieve a token from the full-node by it's id

        :param id: Token UID
        :type id: str
        """
        response = self.hathor_core_client.get(TOKEN_ENDPOINT, {"id": id})

        if response is None:
            return None

        token_response = HathorCoreTokenResponse.from_dict(response)

        if not token_response.success:
            return None

        return token_response.to_token(id)
