import json
from typing import Optional

from common.configuration import METADATA_BUCKET
from gateways.clients.s3_client import S3Client


class MetadataGateway:

    def __init__(self, s3_client: Optional[S3Client] = None) -> None:
        self.s3_client = s3_client or S3Client()

    def get_dag_metadata(self, id: str) -> Optional[str]:
        """Retrieve dag metadata from a json file stored in s3

        :param id: dag entity hash id
        :type id: str
        :raises Exception: The name of the bucket used to store the jsons must be on config
        :return: metadata json file contents or None if not found
        :rtype: str | None
        """
        metadata = self._get_metadata(f"dag/{id}.json")
        if metadata is None:
            return None
        return json.dumps({id: metadata})

    def _get_metadata(self, s3_object_name: str) -> Optional[dict]:
        """Retrieve metadata from file in s3

        :param s3_object_name: name of object
        :type s3_object_name: str

        :raises Exception: The name of the bucket used to store the jsons must be on config

        :return: parsed file content (from `json`)
        :rtype: Optional[dict]
        """
        metadata_bucket = self._metadata_bucket()

        raw_metadata = self.s3_client.load_file(metadata_bucket, s3_object_name)
        if raw_metadata is None:
            return None

        try:
            return json.loads(raw_metadata)
        except ValueError:
            return None

    def _metadata_bucket(self) -> str:
        metadata_bucket = METADATA_BUCKET

        if metadata_bucket is None:
            raise Exception('No bucket name in config')

        return metadata_bucket