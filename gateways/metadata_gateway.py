import json
from typing import Optional

from common.configuration import METADATA_BUCKET
from domain.metadata.metadata import MetadataType
from domain.metadata.token_metadata import TokenMetadata
from domain.metadata.transaction_metadata import TransactionMetadata
from gateways.clients.s3_client import S3Client

TYPE_TO_FOLDER = {
    MetadataType.TRANSACTION: 'transaction',
    MetadataType.TOKEN: 'token'
}


class MetadataGateway:

    def __init__(self, s3_client: Optional[S3Client] = None) -> None:
        self.s3_client = s3_client or S3Client()

    def get_transaction_metadata(self, id: str) -> Optional[TransactionMetadata]:
        """Retrieve transaction metadata from a json file stored in s3

        :param id: transaction id
        :type id: str
        :raises Exception: The name of the bucket used to store the jsons must be on config
        :return: TransactionMetadata object or None if not found
        :rtype: TokenMetadata | None
        """
        folder = TYPE_TO_FOLDER[MetadataType.TRANSACTION]
        transaction_metadata = self._get_metadata(f"{folder}/{id}.json")

        if transaction_metadata is None:
            return None

        return TransactionMetadata.from_dict(transaction_metadata)

    def get_token_metadata(self, id: str) -> Optional[TokenMetadata]:
        """Retrieve token metadata from a json file stored in s3

        :param id: token id
        :type id: str

        :return: TokenMetadata object or None if not found
        :rtype: TokenMetadata | None
        """
        folder = TYPE_TO_FOLDER[MetadataType.TOKEN]
        token_metadata = self._get_metadata(f"{folder}/{id}.json")

        if token_metadata is None:
            return None

        return TokenMetadata.from_dict(token_metadata)

    def _get_metadata(self, s3_object_name: str) -> Optional[dict]:
        """Retrive metadata from file in s3

        :param s3_object_name: name of object
        :type s3_object_name: str

        :raises Exception: The name of the bucket used to store the jsons must be on config

        :return: file content as dict
        :rtype: Optional[dict]
        """
        metadata_bucket = self._metadata_bucket()

        raw_metadata = self.s3_client.load_file(metadata_bucket, s3_object_name)
        if raw_metadata is None:
            return None

        return json.loads(raw_metadata)

    def _metadata_bucket(self) -> str:
        metadata_bucket = METADATA_BUCKET

        if metadata_bucket is None:
            raise Exception('No bucket name in config')

        return metadata_bucket
