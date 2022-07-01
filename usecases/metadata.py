from typing import Optional

from gateways.metadata_gateway import MetadataGateway


class Metadata:

    def __init__(self, metadata_gateway: Optional[MetadataGateway] = None) -> None:
        self.metadata_gateway = metadata_gateway or MetadataGateway()

    def get(self, type: str, id: str) -> Optional[str]:
        # Multiple metadatas can be obtained at once here
        metadata_methods = {
            'dag': self.metadata_gateway.get_dag_metadata,
        }
        method = metadata_methods.get(type, None)
        if method is None:
            return None

        return method(id)

    def put_dag(self, type: str, id: str, content: dict) -> None:
        # Only the dag metadata will be updated here
        return self.metadata_gateway.put_dag_metadata(id, content)
