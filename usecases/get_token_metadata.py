from typing import Optional

from gateways.metadata_gateway import MetadataGateway


class GetTokenMetadata:
    """Get token metadata

    :deprecated:
    """

    def __init__(self, metadata_gateway: Optional[MetadataGateway] = None) -> None:
        self.metadata_gateway = metadata_gateway or MetadataGateway()

    def get(self, id: str) -> Optional[dict]:
        meta = self.metadata_gateway.get_token_metadata(id)

        if meta:
            return meta.to_dict()['data']

        return None
