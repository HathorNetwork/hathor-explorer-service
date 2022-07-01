from typing import Optional

from gateways.metadata_gateway import MetadataGateway


class PutMetadata:

    def __init__(self, metadata_gateway: Optional[MetadataGateway] = None) -> None:
        self.metadata_gateway = metadata_gateway or MetadataGateway()

    def put(self, type: str, id: str, content: dict) -> Optional[str]:
        metadata_methods = {
            'dag': self.metadata_gateway.put_dag_metadata,
        }
        method = metadata_methods.get(type, None)
        if method is None:
            return None

        return method(id, content)
