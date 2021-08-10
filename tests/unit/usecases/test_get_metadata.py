from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.metadata_factory import (
    MetaTokenFactory,
    MetaTransactionFactory,
    TokenMetadataFactory,
    TokenNFTMediaFactory,
    TransactionMetadataFactory,
)
from usecases.get_metadata import GetMetadata


class TestGetMetadata:

    @fixture
    def metadata_gateway(self):
        return MagicMock()

    def test_get_for_token(self, metadata_gateway):
        nft_media = TokenNFTMediaFactory()
        meta_token = MetaTokenFactory(nft_media=nft_media)
        token_metadata = TokenMetadataFactory(id=meta_token.id, data=meta_token)

        metadata_gateway.get_token_metadata = MagicMock(return_value=token_metadata)

        get_token_metadata = GetMetadata(metadata_gateway)

        result = get_token_metadata.get('token', token_metadata.id)

        metadata_gateway.get_token_metadata.assert_called_once_with(token_metadata.id)
        assert result
        assert result['id'] == token_metadata.id
        assert result['data']['verified'] == token_metadata.data.verified
        assert result['data']['banned'] == token_metadata.data.banned
        assert result['data']['nft'] == token_metadata.data.nft
        assert result['data']['nft_media']['file'] == token_metadata.data.nft_media.file
        assert result['data']['nft_media']['loop'] == token_metadata.data.nft_media.loop

    def test_get_for_transaction(self, metadata_gateway):
        meta_transaction = MetaTransactionFactory()
        transaction_metadata = TransactionMetadataFactory(id=meta_transaction.id, data=meta_transaction)

        metadata_gateway.get_transaction_metadata = MagicMock(return_value=transaction_metadata)

        get_transaction_metadata = GetMetadata(metadata_gateway)

        result = get_transaction_metadata.get('transaction', transaction_metadata.id)

        metadata_gateway.get_transaction_metadata.assert_called_once_with(transaction_metadata.id)
        assert result
        assert result['id'] == transaction_metadata.id
        assert result['data']['genesis'] == transaction_metadata.data.genesis
        assert result['data']['context'] == transaction_metadata.data.context

    def test_get_for_others(self, metadata_gateway):
        get_transaction_metadata = GetMetadata(metadata_gateway)

        result = get_transaction_metadata.get('something', 'any-id')

        assert result is None

    def test_get_return_none(self, metadata_gateway):
        metadata_gateway.get_token_metadata = MagicMock(return_value=None)

        get_token_metadata = GetMetadata(metadata_gateway)

        result = get_token_metadata.get('token', 'some-id')

        metadata_gateway.get_token_metadata.assert_called_once_with("some-id")
        assert result is None
