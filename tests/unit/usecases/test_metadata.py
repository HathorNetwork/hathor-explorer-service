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

    def test_put_for_dag(self, metadata_gateway):
        metadata_gateway.put_dag_metadata = MagicMock(return_value=None)

        metadata = Metadata(metadata_gateway)

        result = metadata.put_dag('dag', 'some-id', '{ "id": "some-id" }')

        metadata_gateway.put_dag_metadata.assert_called_once_with('some-id', '{ "id": "some-id" }')
        assert result is None
