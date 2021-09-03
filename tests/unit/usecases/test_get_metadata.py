from unittest.mock import MagicMock

from pytest import fixture

from usecases.get_metadata import GetMetadata


class TestGetMetadata:

    @fixture
    def metadata_gateway(self):
        return MagicMock()

    def test_get_for_dag(self, metadata_gateway):
        metadata_gateway.get_dag_metadata = MagicMock(return_value="some-return")

        get_metadata = GetMetadata(metadata_gateway)

        result = get_metadata.get('dag', 'some-id')

        metadata_gateway.get_dag_metadata.assert_called_once_with('some-id')
        assert result == "some-return"

    def test_get_for_others(self, metadata_gateway):
        get_metadata = GetMetadata(metadata_gateway)

        result = get_metadata.get('something', 'any-id')

        assert result is None

    def test_get_return_none(self, metadata_gateway):
        metadata_gateway.get_dag_metadata = MagicMock(return_value=None)

        get_metadata = GetMetadata(metadata_gateway)

        result = get_metadata.get('dag', 'some-id')

        metadata_gateway.get_dag_metadata.assert_called_once_with("some-id")
        assert result is None
