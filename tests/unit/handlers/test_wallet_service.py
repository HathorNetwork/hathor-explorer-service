import json
from unittest.mock import MagicMock

from faker import Faker
from pytest import fixture, mark

from common.errors import RdsNotFoundError
from handlers.wallet_service import (
    handle_address_balance,
    handle_address_history,
    handle_address_tokens,
)

fake = Faker()


def event(**query: str) -> dict:
    return {"queryStringParameters": query}


class TestHandleAddressHistory:
    @fixture
    def wallet_service(self):
        wallet_service = MagicMock()
        wallet_service.address_history.return_value = {"history": [], "has_next": False}
        wallet_service.address_confidential_history.return_value = {
            "history": [],
            "has_next": True,
        }
        return wallet_service

    def test_token_history(self, wallet_service):
        address = fake.pystr()
        token = fake.sha256()
        last_tx = fake.sha256()

        response = handle_address_history(
            event(
                address=address,
                token=token,
                limit="20",
                last_tx=last_tx,
                last_ts="1234",
            ),
            None,
            wallet_service,
        )

        assert response["statusCode"] == 200
        assert json.loads(response["body"]) == {"history": [], "has_next": False}
        wallet_service.address_history.assert_called_once_with(
            address, token, 20, last_tx, 1234
        )
        wallet_service.address_confidential_history.assert_not_called()

    @mark.parametrize("confidential", [None, "false"])
    def test_token_history_defaults(self, wallet_service, confidential):
        address = fake.pystr()
        token = fake.sha256()
        query = {"address": address, "token": token}
        if confidential is not None:
            query["confidential"] = confidential

        response = handle_address_history(event(**query), None, wallet_service)

        assert response["statusCode"] == 200
        wallet_service.address_history.assert_called_once_with(
            address, token, 10, None, 0
        )

    def test_confidential_history(self, wallet_service):
        address = fake.pystr()
        last_tx = fake.sha256()

        response = handle_address_history(
            event(
                address=address,
                confidential="true",
                limit="5",
                last_tx=last_tx,
                last_ts="99",
            ),
            None,
            wallet_service,
        )

        assert response["statusCode"] == 200
        assert json.loads(response["body"]) == {"history": [], "has_next": True}
        wallet_service.address_confidential_history.assert_called_once_with(
            address, 5, last_tx, 99
        )
        wallet_service.address_history.assert_not_called()

    @mark.parametrize(
        "query",
        [
            # No address
            {"token": "00"},
            {"confidential": "true"},
            # Neither a token nor the confidential history
            {"address": "addr"},
            {"address": "addr", "confidential": "false"},
            # Both a token and the confidential history
            {"address": "addr", "token": "00", "confidential": "true"},
            # Not a boolean
            {"address": "addr", "confidential": "1"},
            {"address": "addr", "token": "00", "confidential": "True"},
            # Bad paging
            {"address": "addr", "token": "00", "limit": "0"},
            {"address": "addr", "token": "00", "limit": "-1"},
            {"address": "addr", "token": "00", "limit": "101"},
            {"address": "addr", "token": "00", "limit": "ten"},
            {"address": "addr", "confidential": "true", "limit": "0"},
            {"address": "addr", "token": "00", "last_ts": "-1"},
            {"address": "addr", "token": "00", "last_ts": "now"},
        ],
    )
    def test_invalid_parameters(self, wallet_service, query):
        response = handle_address_history(event(**query), None, wallet_service)

        assert response["statusCode"] == 400
        assert json.loads(response["body"]) == {"error": "invalid_parameters"}
        wallet_service.address_history.assert_not_called()
        wallet_service.address_confidential_history.assert_not_called()

    @mark.parametrize("limit", ["1", "100"])
    def test_limit_bounds(self, wallet_service, limit):
        response = handle_address_history(
            event(address="addr", token="00", limit=limit), None, wallet_service
        )

        assert response["statusCode"] == 200


class TestHandleAddressBalance:
    def test_balance(self):
        wallet_service = MagicMock()
        wallet_service.address_balance.return_value = {"token_id": "00"}

        response = handle_address_balance(
            event(address="addr", token="00"), None, wallet_service
        )

        assert response["statusCode"] == 200
        assert json.loads(response["body"]) == {"token_id": "00"}
        wallet_service.address_balance.assert_called_once_with("addr", "00")

    def test_not_found(self):
        wallet_service = MagicMock()
        wallet_service.address_balance.side_effect = RdsNotFoundError("not found")

        response = handle_address_balance(
            event(address="addr", token="00"), None, wallet_service
        )

        assert response["statusCode"] == 404

    @mark.parametrize("query", [{"address": "addr"}, {"token": "00"}])
    def test_invalid_parameters(self, query):
        wallet_service = MagicMock()

        response = handle_address_balance(event(**query), None, wallet_service)

        assert response["statusCode"] == 400
        wallet_service.address_balance.assert_not_called()


class TestHandleAddressTokens:
    def test_tokens(self):
        wallet_service = MagicMock()
        body = {
            "total": 0,
            "tokens": {},
            "has_confidential_activity": False,
            "has_hidden_token_activity": False,
        }
        wallet_service.address_tokens.return_value = body

        response = handle_address_tokens(
            event(address="addr", limit="3", offset="6"), None, wallet_service
        )

        assert response["statusCode"] == 200
        assert json.loads(response["body"]) == body
        wallet_service.address_tokens.assert_called_once_with("addr", 3, 6)

    @mark.parametrize(
        "query",
        [{}, {"address": "addr", "limit": "101"}, {"address": "addr", "offset": "x"}],
    )
    def test_invalid_parameters(self, query):
        wallet_service = MagicMock()

        response = handle_address_tokens(event(**query), None, wallet_service)

        assert response["statusCode"] == 400
        wallet_service.address_tokens.assert_not_called()
