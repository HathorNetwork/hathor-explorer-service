import json
from unittest.mock import MagicMock, patch

import pytest
from gateways.token_gateway import TokenGateway
from pytest import fixture

from tests.fixtures.token_factory import TokenMetadataFactory, TokenNFTFactory


class TestTokenGateway:

    @fixture
    def s3_client(self):
        return MagicMock()

    @patch('gateways.token_gateway.TOKEN_METADATA_BUCKET', 'token-metadata')
    def test_get_token_metadata_from_s3(self, s3_client):
        nft = TokenNFTFactory()
        token_metadata = TokenMetadataFactory(nft=nft)

        s3_client.load_file = MagicMock(return_value=json.dumps(token_metadata.to_dict()))

        gateway = TokenGateway(s3_client=s3_client)

        result = gateway.get_token_metadata_from_s3('token-id')

        s3_client.load_file.assert_called_once_with('token-metadata', 'token-id')
        assert result
        assert result.id == token_metadata.id
        assert result.verified == token_metadata.verified
        assert result.banned == token_metadata.banned
        assert result.reason == token_metadata.reason
        assert result.nft.file == token_metadata.nft.file
        assert result.nft.type == token_metadata.nft.type

    @patch('gateways.token_gateway.TOKEN_METADATA_BUCKET', 'token-metadata')
    def test_get_token_metadata_from_s3_return_none(self, s3_client):
        s3_client.load_file = MagicMock(return_value=None)

        gateway = TokenGateway(s3_client=s3_client)

        result = gateway.get_token_metadata_from_s3('token-id')

        s3_client.load_file.assert_called_once_with('token-metadata', 'token-id')

        assert result is None

    @patch('gateways.token_gateway.TOKEN_METADATA_BUCKET', None)
    def test_get_token_metadata_from_s3_raises_exception(self):
        gateway = TokenGateway()

        with pytest.raises(Exception, match=r'No bucket name in config'):
            gateway.get_token_metadata_from_s3('token-id')
