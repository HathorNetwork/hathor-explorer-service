from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.token_factory import TokenFactory
from usecases.get_token import GetToken


class TestGetToken:

    @fixture
    def token_gateway(self):
        return MagicMock()

    def test_get(self, token_gateway):
        token = TokenFactory()

        token_gateway.get_token = MagicMock(return_value=token)

        get_token = GetToken(token_gateway)

        result = get_token.get(token.id)

        assert result
        assert result['id'] == token.id

    def test_get_not_found(self, token_gateway):
        token_gateway.get_token = MagicMock(return_value=None)

        get_token = GetToken(token_gateway)

        result = get_token.get('abcdef1234567890')

        assert result is None
