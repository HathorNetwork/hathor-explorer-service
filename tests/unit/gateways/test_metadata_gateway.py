import json
from unittest.mock import MagicMock, patch

from pytest import fixture, raises

from gateways.metadata_gateway import MetadataGateway
from tests.fixtures.metadata_factory import TokenMetadataFactory, TokenNFTFactory


class TestMetadataGateway:

    @fixture
    def s3_client(self):
        return MagicMock()

    @patch('gateways.metadata_gateway.METADATA_BUCKET', 'metadata')
    def test_get_token_metadata(self, s3_client):
        nft = TokenNFTFactory()
        token_metadata = TokenMetadataFactory(nft=nft)

        s3_client.load_file = MagicMock(return_value=json.dumps(token_metadata.to_dict()))

        gateway = MetadataGateway(s3_client=s3_client)

        result = gateway.get_token_metadata('token-id')

        s3_client.load_file.assert_called_once_with('metadata', 'token-id')
        assert result
        assert result.id == token_metadata.id
        assert result.verified == token_metadata.verified
        assert result.banned == token_metadata.banned
        assert result.reason == token_metadata.reason
        assert result.nft.file == token_metadata.nft.file
        assert result.nft.type == token_metadata.nft.type

    @patch('gateways.metadata_gateway.METADATA_BUCKET', 'metadata')
    def test_get_token_metadata_return_none(self, s3_client):
        s3_client.load_file = MagicMock(return_value=None)

        gateway = MetadataGateway(s3_client=s3_client)

        result = gateway.get_token_metadata('token-id')

        s3_client.load_file.assert_called_once_with('metadata', 'token-id')

        assert result is None

    @patch('gateways.metadata_gateway.METADATA_BUCKET', None)
    def test_get_token_metadata_raises_exception(self):
        gateway = MetadataGateway()

        with raises(Exception, match=r'No bucket name in config'):
            gateway.get_token_metadata('token-id')
