from typing import Union

from gateways.token_gateway import TokenGateway


class GetToken:

    def __init__(self, token_gateway: Union[TokenGateway, None] = None) -> None:
        self.token_gateway = token_gateway or TokenGateway()

    def get(self, id: str) -> Union[dict, None]:
        token = self.token_gateway.get_token(id)

        if token:
            return token.to_dict()

        return None
