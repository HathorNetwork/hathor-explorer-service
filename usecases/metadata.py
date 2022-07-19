from typing import Optional
import json

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

    def create_or_update_dag(self, txhash: str, update_data: str) -> None:
        # Convert both JSONs into dicts
        existing = json.loads(self.metadata_gateway.get_dag_metadata(txhash) or '{}')
        inputted = json.loads(update_data)

        # Merge the existing and input metadata, with the input having priority
        new_content = {**existing, **inputted}

        # Call the existing put_dag_metadata with the string version of the merged object
        return self.metadata_gateway.put_dag_metadata(txhash, json.dumps(new_content))
