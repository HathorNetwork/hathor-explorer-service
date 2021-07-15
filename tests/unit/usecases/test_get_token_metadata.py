from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.metadata_factory import MetaTokenFactory, TokenMetadataFactory, TokenNFTFactory
from usecases.get_token_metadata import GetTokenMetadata


class TestGetTokenMetadata:

    @fixture
    def token_gateway(self):
        return MagicMock()

    def test_get(self, token_gateway):
        nft = TokenNFTFactory()
        meta_token = MetaTokenFactory(nft=nft)
        token_metadata = TokenMetadataFactory(id=meta_token.id, data=meta_token)

        token_gateway.get_token_metadata = MagicMock(return_value=token_metadata)

        get_token_metadata = GetTokenMetadata(token_gateway)

        result = get_token_metadata.get(token_metadata.id)

        token_gateway.get_token_metadata.assert_called_once_with(token_metadata.id)
        assert result
        assert result['id'] == token_metadata.id
        assert result['verified'] == token_metadata.data.verified
        assert result['banned'] == token_metadata.data.banned
        assert result['nft']['file'] == token_metadata.data.nft.file

    def test_get_return_none(self, token_gateway):
        token_gateway.get_token_metadata = MagicMock(return_value=None)

        get_token_metadata = GetTokenMetadata(token_gateway)

        result = get_token_metadata.get('some-id')

        token_gateway.get_token_metadata.assert_called_once_with("some-id")
        assert result is None
