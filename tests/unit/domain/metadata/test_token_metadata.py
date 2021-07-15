from domain.metadata.token_metadata import TokenMetadata
from tests.fixtures.metadata_factory import TokenMetadataFactory, TokenNFTFactory, MetaTokenFactory


class TestTokenMetadata:

    def test_token_metadata_to_dict(self):
        nft = TokenNFTFactory()
        meta_token = MetaTokenFactory(nft=nft)
        token_metadata = TokenMetadataFactory(data=meta_token)

        token_metadata_dict = token_metadata.to_dict()

        assert token_metadata_dict
        assert token_metadata_dict['id'] == token_metadata.id
        assert token_metadata_dict['data']['banned'] == token_metadata.data.banned
        assert token_metadata_dict['data']['nft']['type'] == token_metadata.data.nft.type.value
        assert token_metadata_dict['data']['nft']['file'] == token_metadata.data.nft.file

    def test_token_metadata_from_dict(self):
        nft = TokenNFTFactory()
        meta_token = MetaTokenFactory(nft=nft)
        token_metadata = TokenMetadataFactory(data=meta_token)

        token_metadata_dict = token_metadata.to_dict()

        new_token_metadata = TokenMetadata.from_dict(token_metadata_dict)

        assert new_token_metadata
        assert new_token_metadata.id == token_metadata.id
        assert new_token_metadata.data.verified == token_metadata.data.verified
        assert new_token_metadata.data.reason == token_metadata.data.reason
        assert new_token_metadata.data.nft.type == token_metadata.data.nft.type
        assert new_token_metadata.data.nft.file == token_metadata.data.nft.file
