from domain.metadata.metadata import Metadata
from pytest import raises


class TestMetadata:

    def test_class_structure(self):
        metadata = Metadata(id='some-id')

        assert metadata.id == 'some-id'

        with raises(NotImplementedError):
            metadata.type

        with raises(NotImplementedError):
            metadata.data

        with raises(NotImplementedError):
            Metadata.from_dict({})

    def test_to_dict(self):
        metadata = Metadata(id='idzin')
        metdata_dict = metadata.to_dict()

        assert metdata_dict['id'] == metadata.id
