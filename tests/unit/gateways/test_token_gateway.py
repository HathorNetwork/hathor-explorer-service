from unittest.mock import MagicMock

from pytest import fixture

from gateways.token_gateway import TokenGateway
from tests.fixtures.hathor_core_fixtures import HATHOR_CORE_GET_TOKEN, HATHOR_CORE_GET_TOKEN_INVALID


class TestTokenGateway:

    @fixture
    def hathor_core_client(self):
        return MagicMock()

    def test_get_token(self, hathor_core_client):
        hathor_core_client.get = MagicMock(return_value=HATHOR_CORE_GET_TOKEN)

        gateway = TokenGateway(hathor_core_client=hathor_core_client)

        token_id = '0058dacaa9cb6e120e825fa40f738273f3bf87e82c8b376158695a4fb42e187d'

        token = gateway.get_token(token_id)

        hathor_core_client.get.assert_called_once_with('/v1a/thin_wallet/token', {'id': token_id})

        assert token
        assert token.id == token_id
        assert token.name == 'HTR Token'
        assert token.symbol == 'TOKEN'
        assert token.total_supply == 10000000
        assert token.transactions_count == 11
        assert token.can_melt is True
        assert token.can_mint is True

    def test_get_token_invalid(self, hathor_core_client):
        hathor_core_client.get = MagicMock(return_value=HATHOR_CORE_GET_TOKEN_INVALID)

        gateway = TokenGateway(hathor_core_client=hathor_core_client)

        token = gateway.get_token('something')

        hathor_core_client.get.assert_called_once_with('/v1a/thin_wallet/token', {'id': 'something'})

        assert token is None

    def test_get_token_no_200(self, hathor_core_client):
        hathor_core_client.get = MagicMock(return_value=None)

        gateway = TokenGateway(hathor_core_client=hathor_core_client)

        token = gateway.get_token('something')

        hathor_core_client.get.assert_called_once_with('/v1a/thin_wallet/token', {'id': 'something'})

        assert token is None
