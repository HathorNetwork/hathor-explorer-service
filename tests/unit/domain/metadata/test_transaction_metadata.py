from domain.metadata.transaction_metadata import TransactionMetadata
from tests.fixtures.metadata_factory import MetaTransactionFactory, TransactionMetadataFactory


class TestTransactionMetadata:

    def test_transaction_metadata_to_dict(self):
        meta_token = MetaTransactionFactory()
        transaction_metadata = TransactionMetadataFactory(id=meta_token.id, data=meta_token)

        transaction_metadata_dict = transaction_metadata.to_dict()

        assert transaction_metadata_dict
        assert transaction_metadata_dict['id'] == transaction_metadata.id
        assert transaction_metadata_dict['data']['context'] == transaction_metadata.data.context
        assert transaction_metadata_dict['data']['genesis'] == transaction_metadata.data.genesis

    def test_transaction_metadata_from_dict(self):
        meta_token = MetaTransactionFactory()
        transaction_metadata = TransactionMetadataFactory(id=meta_token.id, data=meta_token)

        transaction_metadata_dict = transaction_metadata.to_dict()

        new_transaction_metadata = TransactionMetadata.from_dict(transaction_metadata_dict)

        assert new_transaction_metadata
        assert new_transaction_metadata.id == transaction_metadata.id
        assert new_transaction_metadata.data.context == transaction_metadata.data.context
        assert new_transaction_metadata.data.genesis == transaction_metadata.data.genesis
