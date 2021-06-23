import pytest

from gateways.clients.responses.hathor_core.hathor_core_token_response import HathorCoreTokenResponse
from tests.fixtures.hathor_core_fixtures import HATHOR_CORE_GET_TOKEN, HATHOR_CORE_GET_TOKEN_INVALID


class TestHathorCoreTokenResponse:

    def test_from_dict(self):
        token_response = HathorCoreTokenResponse.from_dict(HATHOR_CORE_GET_TOKEN)

        expected_tx_id = '0058dacaa9cb6e120e825fa40f738273f3bf87e82c8b376158695a4fb42e187d'

        assert token_response
        assert token_response.name == 'HTR Token'
        assert token_response.success is True
        assert token_response.message is None
        assert token_response.symbol == 'TOKEN'
        assert token_response.total == 10000000
        assert token_response.transactions_count == 11
        assert token_response.melt == [{'tx_id': expected_tx_id, 'index': 3}]
        assert token_response.mint == [{'tx_id': expected_tx_id, 'index': 2}]

    def test_from_dict_invalid(self):
        token_response = HathorCoreTokenResponse.from_dict(HATHOR_CORE_GET_TOKEN_INVALID)

        assert token_response
        assert token_response.name is None
        assert token_response.success is False
        assert token_response.message == 'Unknown token'
        assert token_response.symbol is None
        assert token_response.total is None
        assert token_response.transactions_count is None
        assert token_response.melt is None
        assert token_response.mint is None

    def test_to_token(self):
        token_response = HathorCoreTokenResponse.from_dict(HATHOR_CORE_GET_TOKEN)

        token_id = '0058dacaa9cb6e120e825fa40f738273f3bf87e82c8b376158695a4fb42e187d'
        token = token_response.to_token(token_id)

        assert token
        assert token.id == token_id
        assert token.name == 'HTR Token'
        assert token.symbol == 'TOKEN'
        assert token.total_supply == 10000000
        assert token.transactions_count == 11
        assert token.can_melt is True
        assert token.can_mint is True

    def test_to_token_invalid_raises(self):
        token_response = HathorCoreTokenResponse.from_dict(HATHOR_CORE_GET_TOKEN_INVALID)

        token_id = '0058dacaa9cb6e120e825fa40f738273f3bf87e82c8b376158695a4fb42abcde'

        with pytest.raises(Exception, match=r'unknown_token'):
            token_response.to_token(token_id)

    def test_to_token_weird_response(self):
        token_response = HathorCoreTokenResponse.from_dict(HATHOR_CORE_GET_TOKEN_INVALID)

        token_response.success = True

        token_id = '0058dacaa9cb6e120e825fa40f738273f3bf87e82c8b376158695a4fb42abcde'

        with pytest.raises(Exception, match=r'malformed_token'):
            token_response.to_token(token_id)
