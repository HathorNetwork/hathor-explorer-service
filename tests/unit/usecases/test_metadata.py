import json
from unittest.mock import MagicMock

from pytest import fixture

from usecases.metadata import Metadata


class TestMetadata:

    @fixture
    def metadata_gateway(self):
        return MagicMock()

    def test_get_for_dag(self, metadata_gateway):
        metadata_gateway.get_dag_metadata = MagicMock(return_value="some-return")

        get_metadata = Metadata(metadata_gateway)

        result = get_metadata.get('dag', 'some-id')

        metadata_gateway.get_dag_metadata.assert_called_once_with('some-id')
        assert result == "some-return"

    def test_get_for_others(self, metadata_gateway):
        get_metadata = Metadata(metadata_gateway)

        result = get_metadata.get('something', 'any-id')

        assert result is None

    def test_get_return_none(self, metadata_gateway):
        metadata_gateway.get_dag_metadata = MagicMock(return_value=None)

        get_metadata = Metadata(metadata_gateway)

        result = get_metadata.get('dag', 'some-id')

        metadata_gateway.get_dag_metadata.assert_called_once_with("some-id")
        assert result is None

    def test_create_or_update_metadata_create(self, metadata_gateway):
        metadata_gateway.get_dag_metadata = MagicMock(return_value=None)
        metadata_gateway.put_dag_metadata = MagicMock(return_value=None)

        metadata = Metadata(metadata_gateway)
        metadata.create_or_update_dag('some-id', '{ "id": "some-id", "nft": true }')

        expected_called_with = json.dumps(dict(id='some-id', nft=True))
        metadata_gateway.put_dag_metadata.assert_called_once_with('some-id', expected_called_with)

    def test_create_or_update_metadata_update_property(self, metadata_gateway):
        metadata_gateway.get_dag_metadata = MagicMock(return_value='{ "id": "some-id", "nft": false }')
        metadata_gateway.put_dag_metadata = MagicMock(return_value=None)

        metadata = Metadata(metadata_gateway)
        metadata.create_or_update_dag('some-id', '{ "id": "some-id", "nft": true }')

        expected_called_with = json.dumps(dict(id='some-id', nft=True))
        metadata_gateway.put_dag_metadata.assert_called_once_with('some-id', expected_called_with)

    def test_create_or_update_metadata_update_new_property(self, metadata_gateway):
        metadata_gateway.get_dag_metadata = MagicMock(return_value='{ "id": "some-id", "nft": false }')
        metadata_gateway.put_dag_metadata = MagicMock(return_value=None)

        metadata = Metadata(metadata_gateway)
        metadata.create_or_update_dag('some-id', '{ "id": "some-id", "new_prop": "some-content" }')

        expected_called_with = json.dumps(dict(id='some-id', nft=False, new_prop='some-content'))
        metadata_gateway.put_dag_metadata.assert_called_once_with('some-id', expected_called_with)
