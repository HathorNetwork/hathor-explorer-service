from unittest.mock import MagicMock

from pytest import fixture

from usecases.token_api import TokenApi


class TestTokenApi:

    @fixture
    def token_api_gateway(self):
        return MagicMock()

    def test_get_tokens(self, token_api_gateway):
        obj = {
            "hits": [
                {
                    "id": "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                    "name": "Test1",
                    "symbol": "TST1",
                    "transaction_timestamp": 1649473276,
                    "sort": [
                        "00000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                        1649473276
                    ],
                    "nft": False
                },
                {
                    "id": "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                    "name": "Test2",
                    "symbol": "TST2",
                    "transaction_timestamp": 1000000000,
                    "sort": [
                        "10000000906db3a2146ec96b452f9ff7431fa273a432d9b14837eb72e17b587a",
                        1000000000
                    ],
                    "nft": False
                }
            ],
            "has_next": False
        }

        token_api_gateway.get_tokens = MagicMock(return_value=obj)

        token_api = TokenApi(token_api_gateway)

        result = token_api.get_tokens("New", "", "", [])
        token_api_gateway.get_tokens.assert_called_once_with("New", "", "", [])
        assert result
        assert sorted(result) == sorted(obj)
