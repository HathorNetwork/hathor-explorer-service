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
                    "id": "00db7e187ab5b247f28d2d50003f6927ca9d856acf5f1610b186cb0fed5b3438",
                    "name": "New New Santos Coin",
                    "symbol": "NNSC",
                    "sort": [
                        "00db7e187ab5b247f28d2d50003f6927ca9d856acf5f1610b186cb0fed5b3438",
                        "New New Santos Coin"
                    ],
                    "nft": True
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
