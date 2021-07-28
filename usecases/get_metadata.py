from typing import Optional

from gateways.metadata_gateway import MetadataGateway


class GetMetadata:

    def __init__(self, metadata_gateway: Optional[MetadataGateway] = None) -> None:
        self.metadata_gateway = metadata_gateway or MetadataGateway()

    def get(self, type: str, id: str) -> Optional[dict]:
        metadata_methods = {
            'token': self.metadata_gateway.get_token_metadata,
            'transaction': self.metadata_gateway.get_transaction_metadata
        }

        meta = None

        method = metadata_methods.get(type, None)

        if method is None:
            return None

        meta = method(id)

        if meta is None:
            return None

        return meta.to_dict()
