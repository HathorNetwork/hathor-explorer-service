from domain.tx.token import TokenMetadata
from tests.fixtures.hathor_core_fixtures import HATHOR_CORE_MAINNET_GET_STATUS, HATHOR_CORE_TESTNET_GET_STATUS
from tests.fixtures.token_factory import TokenMetadataFactory, TokenNFTFactory


class TestToken:

    def test_token_metadata_to_dict(self):
        nft = TokenNFTFactory()
        token_metadata = TokenMetadataFactory(nft=nft)

        token_metadata_dict = token_metadata.to_dict()

        assert token_metadata_dict
        assert token_metadata_dict['id'] == token_metadata.id
        assert token_metadata_dict['banned'] == token_metadata.banned
        assert token_metadata_dict['nft']['type'] == token_metadata.nft.type.value
        assert token_metadata_dict['nft']['file'] == token_metadata.nft.file

    def test_token_metadata_from_dict(self):
        nft = TokenNFTFactory()
        token_metadata = TokenMetadataFactory(nft=nft)

        token_metadata_dict = token_metadata.to_dict()

        new_token_metadata = TokenMetadata.from_dict(token_metadata_dict)

        assert new_token_metadata
        assert new_token_metadata.id == token_metadata.id
        assert new_token_metadata.verified == token_metadata.verified
        assert new_token_metadata.reason == token_metadata.reason
        assert new_token_metadata.nft.type == token_metadata.nft.type
        assert new_token_metadata.nft.file == token_metadata.nft.file
