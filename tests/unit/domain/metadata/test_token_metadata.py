from domain.metadata.token_metadata import TokenMetadata
from tests.fixtures.metadata_factory import MetaTokenFactory, TokenMetadataFactory, TokenNFTMediaFactory


class TestTokenMetadata:

    def test_token_metadata_to_dict(self):
        nft_media = TokenNFTMediaFactory()
        meta_token = MetaTokenFactory(nft_media=nft_media)
        token_metadata = TokenMetadataFactory(data=meta_token)

        token_metadata_dict = token_metadata.to_dict()

        assert token_metadata_dict
        assert token_metadata_dict['id'] == token_metadata.id
        assert token_metadata_dict['data']['banned'] == token_metadata.data.banned
        assert token_metadata_dict['data']['nft'] == token_metadata.data.nft
        assert token_metadata_dict['data']['nft_media']['type'] == token_metadata.data.nft_media.type.value
        assert token_metadata_dict['data']['nft_media']['file'] == token_metadata.data.nft_media.file
        assert token_metadata_dict['data']['nft_media']['loop'] == token_metadata.data.nft_media.loop

    def test_token_metadata_from_dict(self):
        nft_media = TokenNFTMediaFactory()
        meta_token = MetaTokenFactory(nft_media=nft_media)
        token_metadata = TokenMetadataFactory(data=meta_token)

        token_metadata_dict = token_metadata.to_dict()

        new_token_metadata = TokenMetadata.from_dict(token_metadata_dict)

        assert new_token_metadata
        assert new_token_metadata.id == token_metadata.id
        assert new_token_metadata.data.verified == token_metadata.data.verified
        assert new_token_metadata.data.reason == token_metadata.data.reason
        assert new_token_metadata.data.nft == token_metadata.data.nft
        assert new_token_metadata.data.nft_media.type == token_metadata.data.nft_media.type
        assert new_token_metadata.data.nft_media.file == token_metadata.data.nft_media.file
        assert new_token_metadata.data.nft_media.loop == token_metadata.data.nft_media.loop
