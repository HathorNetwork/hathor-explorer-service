from typing import Union

from gateways.metadata_gateway import MetadataGateway


class GetMetadata:

    def __init__(self, metadata_gateway: Union[MetadataGateway, None] = None) -> None:
        self.metadata_gateway = metadata_gateway or MetadataGateway()

    def get(self, type: str, id: str) -> Union[dict, None]:
        metadata_methods = {
            'token': self.metadata_gateway.get_token_metadata,
            'transaction': self.metadata_gateway.get_transaction_metadata
        }

        meta = None

        method = metadata_methods.get(type, None)

        if method:
            meta = method(id)

        if meta:
            return meta.to_dict()

        return None
