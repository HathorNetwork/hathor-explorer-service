from typing import Union

from gateways.token_gateway import TokenGateway


class GetTokenMetadata:

    def __init__(self, token_gateway: Union[TokenGateway, None] = None) -> None:
        self.token_gateway = token_gateway or TokenGateway()

    def get(self, id: str) -> Union[dict, None]:
        meta = self.token_gateway.get_token_metadata_from_s3(f"{id}.json")

        if meta:
            return meta.to_dict()

        return None
