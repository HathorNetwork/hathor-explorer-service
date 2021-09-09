from domain.tx.token import Token
from tests.fixtures.token_factory import TokenFactory


class TestToken:

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
