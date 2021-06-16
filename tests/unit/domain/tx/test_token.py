from domain.tx.token import Token, TokenMetadata
from tests.fixtures.token_factory import TokenFactory, TokenMetadataFactory, TokenNFTFactory


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

    def test_token_to_dict(self):
        token = TokenFactory()

        token_dict = token.to_dict()

        assert token_dict
        assert token_dict['name'] == token.name
        assert token_dict['symbol'] == token.symbol
        assert token_dict['total_supply'] == token.total_supply
        assert token_dict['transactions_count'] == token.transactions_count
        assert token_dict['can_mint'] == token.can_mint
        assert token_dict['can_melt'] == token.can_melt

    def test_token_from_dict(self):
        token = TokenFactory()

        token_dict = token.to_dict()

        new_token = Token.from_dict(token_dict)

        assert new_token
        assert new_token.name == token.name
        assert new_token.symbol == token.symbol
        assert new_token.total_supply == token.total_supply
        assert new_token.transactions_count == token.transactions_count
        assert new_token.can_mint == token.can_mint
        assert new_token.can_melt == token.can_melt
