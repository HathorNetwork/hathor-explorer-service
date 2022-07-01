import json
from typing import Optional

from common.configuration import METADATA_BUCKET
from common.errors import ConfigError
from common.logging import get_logger
from gateways.clients.s3_client import S3Client

logger = get_logger()


class MetadataGateway:

    def __init__(self, s3_client: Optional[S3Client] = None) -> None:
        self.s3_client = s3_client or S3Client()

    def get_dag_metadata(self, id: str) -> Optional[str]:
        """Retrieve dag metadata from a json file stored in s3

        :param id: dag entity hash id
        :type id: str
        :raises ConfigError: The name of the bucket used to store the jsons must be on config
        :return: metadata json file contents or None if not found
        :rtype: str | None
        """
        metadata = self._get_metadata(f"dag/{id}.json")
        if metadata is None:
            return None
        return json.dumps({id: metadata})

    def put_dag_metadata(self, id: str, contents: dict) -> str:
        """Update dag metadata on a json file stored in s3, with contents received via parameter

        :param id: dag entity hash id
        :type id: str
        :param contents: dictionary with the dag metadata contents for this hash id
        :type contents: dict
        :raises ConfigError: The name of the bucket used to store the jsons must be on config
        :return: None. No need to pass along the S3 upload metadata.
        :rtype: None
        """
        self._update_metadata(id, contents)

    def _get_metadata(self, s3_object_name: str) -> Optional[dict]:
        """Retrieve metadata from file in s3

        :param s3_object_name: name of object
        :type s3_object_name: str

        :raises ConfigError: The name of the bucket used to store the jsons must be on config

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
            logger.warning('Metadata object {} is not a valid json'.format(s3_object_name))
            return None

    def _metadata_bucket(self) -> str:
        """Get metadata bucket name

        :raises ConfigError: The name of the bucket used to store the jsons must be on config

        :return: metadata bucket name
        :rtype: str
        """
        metadata_bucket = METADATA_BUCKET

        if metadata_bucket is None:
            raise ConfigError('No bucket name in config')

        return metadata_bucket

    def _update_metadata(self, tokenUid: str, metadata: dict) -> Optional[dict]:
        """Update a token's metadata and returns it as a response

        :param tokenUid: Token UID
        :type tokenUid: str

        :param metadata: Token metadata
        :type metadata: Object

        :return: S3 Upload metadata
        :rtype: dict
        """
        response = self.s3_client.upload_file(
            self._metadata_bucket(),
            f"dag/{tokenUid}.json",
            json.dumps(metadata),  # type: ignore[arg-type]
        )

        return response
