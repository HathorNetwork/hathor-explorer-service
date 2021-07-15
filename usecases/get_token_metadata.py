from typing import Union

from gateways.metadata_gateway import MetadataGateway


class GetTokenMetadata:

    def __init__(self, metadata_gateway: Union[MetadataGateway, None] = None) -> None:
        self.metadata_gateway = metadata_gateway or MetadataGateway()

    def get(self, id: str) -> Union[dict, None]:
        meta = self.metadata_gateway.get_token_metadata(id)

        if meta:
            return meta.to_dict()['data']

        return None
