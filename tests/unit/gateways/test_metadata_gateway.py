import json
from unittest.mock import MagicMock, patch

from pytest import fixture, raises

from gateways.metadata_gateway import MetadataGateway
from tests.fixtures.metadata_factory import (
    MetaTokenFactory,
    MetaTransactionFactory,
    TokenMetadataFactory,
    TokenNFTMediaFactory,
    TransactionMetadataFactory,
)


class TestMetadataGateway:

    @fixture
    def s3_client(self):
        return MagicMock()

    @patch('gateways.metadata_gateway.METADATA_BUCKET', 'metadata')
    def test_get_token_metadata(self, s3_client):
        nft_media = TokenNFTMediaFactory()
        meta_token = MetaTokenFactory(nft_media=nft_media)
        token_metadata = TokenMetadataFactory(data=meta_token)

        s3_client.load_file = MagicMock(return_value=json.dumps(token_metadata.to_dict()))

        gateway = MetadataGateway(s3_client=s3_client)

        result = gateway.get_token_metadata('token-id')

        s3_client.load_file.assert_called_once_with('metadata', 'token/token-id.json')
        assert result
        assert result.id == token_metadata.id
        assert result.data.verified == token_metadata.data.verified
        assert result.data.banned == token_metadata.data.banned
        assert result.data.nft == token_metadata.data.nft
        assert result.data.reason == token_metadata.data.reason
        assert result.data.nft_media.file == token_metadata.data.nft_media.file
        assert result.data.nft_media.type == token_metadata.data.nft_media.type
        assert result.data.nft_media.loop == token_metadata.data.nft_media.loop

    @patch('gateways.metadata_gateway.METADATA_BUCKET', 'metadata')
    def test_get_token_metadata_return_none(self, s3_client):
        s3_client.load_file = MagicMock(return_value=None)

        gateway = MetadataGateway(s3_client=s3_client)

        result = gateway.get_token_metadata('token-id')

        s3_client.load_file.assert_called_once_with('metadata', 'token/token-id.json')

        assert result is None

    @patch('gateways.metadata_gateway.METADATA_BUCKET', None)
    def test_get_token_metadata_raises_exception(self):
        gateway = MetadataGateway()

        with raises(Exception, match=r'No bucket name in config'):
            gateway.get_token_metadata('token-id')

    @patch('gateways.metadata_gateway.METADATA_BUCKET', 'metadata')
    def test_get_transaction_metadata(self, s3_client):
        meta_transaction = MetaTransactionFactory()
        transaction_metadata = TransactionMetadataFactory(id=meta_transaction.id, data=meta_transaction)

        s3_client.load_file = MagicMock(return_value=json.dumps(transaction_metadata.to_dict()))

        gateway = MetadataGateway(s3_client=s3_client)

        result = gateway.get_transaction_metadata('transaction-id')

        s3_client.load_file.assert_called_once_with('metadata', 'transaction/transaction-id.json')
        assert result
        assert result.id == transaction_metadata.id
        assert result.data.genesis == transaction_metadata.data.genesis
        assert result.data.context == transaction_metadata.data.context

    @patch('gateways.metadata_gateway.METADATA_BUCKET', 'metadata')
    def test_get_transaction_metadata_return_none(self, s3_client):
        s3_client.load_file = MagicMock(return_value=None)

        gateway = MetadataGateway(s3_client=s3_client)

        result = gateway.get_transaction_metadata('transaction-id')

        s3_client.load_file.assert_called_once_with('metadata', 'transaction/transaction-id.json')

        assert result is None

    @patch('gateways.metadata_gateway.METADATA_BUCKET', None)
    def test_get_transaction_metadata_raises_exception(self):
        gateway = MetadataGateway()

        with raises(Exception, match=r'No bucket name in config'):
            gateway.get_transaction_metadata('transaction-id')
