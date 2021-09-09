import json
from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.metadata_factory import TokenMetadataFactory
from usecases.get_token_metadata import GetTokenMetadata


class TestGetTokenMetadata:

    @fixture
    def metadata_gataway(self):
        return MagicMock()

    def test_get(self, metadata_gataway):
        token_metadata = TokenMetadataFactory()
        hash_id = token_metadata["id"]
        metadata_gataway.get_dag_metadata = MagicMock(return_value=json.dumps({hash_id: token_metadata}))

        get_token_metadata = GetTokenMetadata(metadata_gataway)

        result = get_token_metadata.get(hash_id)

        metadata_gataway.get_dag_metadata.assert_called_once_with(hash_id)
        assert result
        assert result['id'] == token_metadata['id']
        assert result.get('verified') == token_metadata.get('verified')
        assert result.get('banned') == token_metadata.get('banned')

    def test_get_return_none(self, metadata_gataway):
        metadata_gataway.get_dag_metadata = MagicMock(return_value=None)

        get_token_metadata = GetTokenMetadata(metadata_gataway)

        result = get_token_metadata.get('some-id')

        metadata_gataway.get_dag_metadata.assert_called_once_with('some-id')
        assert result is None
