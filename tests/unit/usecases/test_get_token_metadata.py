from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.token_factory import TokenMetadataFactory
from usecases.get_token_metadata import GetTokenMetadata


class TestGetTokenMetadata:

    @fixture
    def token_gateway(self):
        return MagicMock()

    def test_get(self, token_gateway):
        token_metadata = TokenMetadataFactory()
        token_metadata_dict = token_metadata.to_dict()
        token_gateway.get_token_metadata_from_s3 = MagicMock(return_value=token_metadata)

        get_token_metadata = GetTokenMetadata(token_gateway)

        result = get_token_metadata.get(token_metadata.id)

        token_gateway.get_token_metadata_from_s3.assert_called_once_with(f"{token_metadata.id}.json")
        assert result
        assert result['id'] == token_metadata_dict['id']
        assert result['verified'] == token_metadata_dict['verified']
        assert result['banned'] == token_metadata_dict['banned']

    def test_get_return_none(self, token_gateway):
        token_gateway.get_token_metadata_from_s3 = MagicMock(return_value=None)

        get_token_metadata = GetTokenMetadata(token_gateway)

        result = get_token_metadata.get('some-id')

        token_gateway.get_token_metadata_from_s3.assert_called_once_with("some-id.json")
        assert result is None
