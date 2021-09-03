import json
from unittest.mock import MagicMock, patch

from pytest import fixture, raises

from gateways.metadata_gateway import MetadataGateway
from tests.fixtures.metadata_factory import TokenMetadataFactory, TransactionMetadataFactory


class TestMetadataGateway:

    @fixture
    def s3_client(self):
        return MagicMock()

    @patch('gateways.metadata_gateway.METADATA_BUCKET', 'metadata')
    def test_get_token_metadata(self, s3_client):
        token_metadata = TokenMetadataFactory()
        hash_id = token_metadata['id']

        s3_client.load_file = MagicMock(return_value=json.dumps(token_metadata))

        gateway = MetadataGateway(s3_client=s3_client)

        result = gateway.get_dag_metadata(hash_id)
        assert result

        s3_client.load_file.assert_called_once_with('metadata', f"dag/{hash_id}.json")

        obj = json.loads(result)
        assert obj
        assert isinstance(obj, dict)
        for key, item in obj.items():
            # key MUST be the entity id, and it must be the generated one
            assert key == item['id'] == token_metadata['id']
            assert item['verified'] == token_metadata['verified']
            assert item['banned'] == token_metadata['banned']
            assert item['nft'] == token_metadata['nft']
            assert item['reason'] == token_metadata['reason']
            if token_metadata['nft_media'] is not None:
                assert item['nft_media']['file'] == token_metadata['nft_media']['file']
                assert item['nft_media']['type'] == token_metadata['nft_media']['type']
                assert item['nft_media']['loop'] == token_metadata['nft_media']['loop']
                assert item['nft_media']['autoplay'] == token_metadata['nft_media']['autoplay']

    @patch('gateways.metadata_gateway.METADATA_BUCKET', 'metadata')
    def test_get_transaction_metadata(self, s3_client):
        transaction_metadata = TransactionMetadataFactory()
        hash_id = transaction_metadata['id']

        s3_client.load_file = MagicMock(return_value=json.dumps(transaction_metadata))

        gateway = MetadataGateway(s3_client=s3_client)

        result = gateway.get_dag_metadata(hash_id)
        assert result

        s3_client.load_file.assert_called_once_with('metadata', f"dag/{hash_id}.json")

        obj = json.loads(result)
        assert obj
        assert isinstance(obj, dict)
        for key, item in obj.items():
            # key MUST be the entity id, and it must be the generated one
            assert key == item['id'] == transaction_metadata['id']
            assert item['genesis'] == transaction_metadata['genesis']
            assert item['context'] == transaction_metadata['context']

    @patch('gateways.metadata_gateway.METADATA_BUCKET', 'metadata')
    def test_get_dag_metadata_return_none(self, s3_client):
        s3_client.load_file = MagicMock(return_value=None)

        gateway = MetadataGateway(s3_client=s3_client)

        result = gateway.get_dag_metadata('dag-id')

        s3_client.load_file.assert_called_once_with('metadata', 'dag/dag-id.json')

        assert result is None

    @patch('gateways.metadata_gateway.METADATA_BUCKET', None)
    def test_get_dag_metadata_raises_exception(self):
        gateway = MetadataGateway()

        with raises(Exception, match=r'No bucket name in config'):
            gateway.get_dag_metadata('token-id')
