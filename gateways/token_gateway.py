import json
from typing import Union

from common.configuration import TOKEN_METADATA_BUCKET
from domain.tx.token import Token, TokenMetadata
from gateways.clients.hathor_core_client import TOKEN_ENDPOINT, HathorCoreClient
from gateways.clients.responses.hathor_core.hathor_core_token_response import HathorCoreTokenResponse
from gateways.clients.s3_client import S3Client


class TokenGateway:
    """Gateway for Token

    :param s3_client: Client for s3 manipulation, default to domain S3Client
    :type s3_client:
    """
    def __init__(
        self,
        s3_client: Union[S3Client, None] = None,
        hathor_core_client: Union[HathorCoreClient, None] = None
    ) -> None:
        self.s3_client = s3_client or S3Client()
        self.hathor_core_client = hathor_core_client or HathorCoreClient()

    def get_token_metadata_from_s3(self, file: str) -> Union[TokenMetadata, None]:
        """Retrieve token metadata from a json file stored in s3

        :param file: file name
        :type file: str
        :raises Exception: The name of the bucket used to store the jsons must be on config
        :return: TokenMetadata object
        :rtype: TokenMetadata
        """
        token_metadata_bucket = TOKEN_METADATA_BUCKET

        if token_metadata_bucket is None:
            raise Exception('No bucket name in config')

        token_raw_metadata = self.s3_client.load_file(token_metadata_bucket, file)
        if token_raw_metadata is None:
            return None

        token_metadata = json.loads(token_raw_metadata)
        return TokenMetadata.from_dict(token_metadata)

    def get_token(self, id: str) -> Union[Token, None]:
        response = self.hathor_core_client.get(TOKEN_ENDPOINT, {'id': id})

        if response is None:
            return None

        token_response = HathorCoreTokenResponse.from_dict(response)

        if not token_response.success:
            return None

        return token_response.to_token(id)
