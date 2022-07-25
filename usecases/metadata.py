import json
from typing import Any, Optional

from gateways.metadata_gateway import MetadataGateway


class Metadata:

    def __init__(self, metadata_gateway: Optional[MetadataGateway] = None) -> None:
        self.metadata_gateway = metadata_gateway or MetadataGateway()

    def get(self, type: str, id: str) -> Optional[str]:
        metadata_methods = {
            'dag': self.metadata_gateway.get_dag_metadata,
        }
        method = metadata_methods.get(type, None)
        if method is None:
            return None

        return method(id)

    def create_or_update_dag(self, id: str, update_data: Any) -> None:
        # Convert both JSONs into dicts
        existing = json.loads(self.metadata_gateway.get_dag_metadata(id) or '{}')

        # Merge the existing and input metadata, with the input having priority
        new_content = {**existing, **update_data}

        # Call the existing put_dag_metadata with the string version of the merged object
        return self.metadata_gateway.put_dag_metadata(id, json.dumps(new_content))
