import json
from typing import Optional

from gateways.metadata_gateway import MetadataGateway


class GetTokenMetadata:
    """Get token metadata

    :deprecated:
    """

    def __init__(self, metadata_gateway: Optional[MetadataGateway] = None) -> None:
        self.metadata_gateway = metadata_gateway or MetadataGateway()

    def get(self, id: str) -> Optional[dict]:
        meta_raw = self.metadata_gateway.get_dag_metadata(id)
        if meta_raw is None:
            return None

        meta = json.loads(meta_raw)
        if meta:
            data = meta[id]
            data['nft'] = data.pop('nft_media')

            return data

        return None
