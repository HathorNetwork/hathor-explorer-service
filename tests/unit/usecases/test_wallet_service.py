from unittest.mock import MagicMock

from faker import Faker
from pytest import fixture, raises

from common.errors import ApiError
from tests.fixtures.wallet_service_factory import (
    TokenBalanceFactory,
    TokenEntryFactory,
    TxHistoryEntryFactory,
)
from usecases.wallet_service import WalletService

fake = Faker()


class TestWalletService:
    @fixture
    def wallet_service_gateway(self):
        gateway = MagicMock()
        gateway.is_reserved_token.return_value = False
        return gateway

    def test_address_balance(self, wallet_service_gateway):
        obj = TokenBalanceFactory()
        wallet_service_gateway.address_balance.return_value = obj

        addr = fake.pystr()
        token = fake.sha256()

        ws = WalletService(wallet_service_gateway)

        assert ws.address_balance(addr, token) == obj.to_dict()
        wallet_service_gateway.address_balance.assert_called_once_with(addr, token)

    def test_address_history(self, wallet_service_gateway):
        return_obj = {
            "history": [
                TxHistoryEntryFactory().to_dict()
                for _ in range(fake.random_int(min=1, max=10))
            ],
            "has_next": True,
        }

        wallet_service_gateway.address_history.return_value = return_obj

        addr = fake.pystr()
        token = fake.sha256()
        limit = fake.pyint()
        last_tx = fake.sha256()
        last_ts = fake.pyint()

        ws = WalletService(wallet_service_gateway)

        expected_history = return_obj["history"]
        returned = ws.address_history(addr, token, limit, last_tx, last_ts)["history"]

        assert len(returned) == len(expected_history)
        assert all([ret == obj for ret, obj in zip(returned, expected_history)])
        wallet_service_gateway.address_history.assert_called_once_with(
            addr, token, limit, last_tx, last_ts
        )

    def test_address_confidential_history(self, wallet_service_gateway):
        return_obj = {
            "history": [
                TxHistoryEntryFactory(token_id=None, balance=None).to_dict()
                for _ in range(fake.random_int(min=1, max=10))
            ],
            "has_next": False,
        }
        wallet_service_gateway.address_confidential_history.return_value = return_obj

        addr = fake.pystr()
        limit = fake.pyint()
        last_tx = fake.sha256()
        last_ts = fake.pyint()

        ws = WalletService(wallet_service_gateway)

        assert ws.address_confidential_history(addr, limit, last_tx, last_ts) == (
            return_obj
        )
        wallet_service_gateway.address_confidential_history.assert_called_once_with(
            addr, limit, last_tx, last_ts
        )

    def test_reserved_token_is_rejected(self, wallet_service_gateway):
        wallet_service_gateway.is_reserved_token.return_value = True

        ws = WalletService(wallet_service_gateway)

        with raises(ApiError, match="invalid_parameters"):
            ws.address_history(fake.pystr(), "reserved", 10, None, 0)
        with raises(ApiError, match="invalid_parameters"):
            ws.address_balance(fake.pystr(), "reserved")

        wallet_service_gateway.address_history.assert_not_called()
        wallet_service_gateway.address_balance.assert_not_called()
        wallet_service_gateway.is_reserved_token.assert_called_with("reserved")

    def test_address_tokens(self, wallet_service_gateway):
        objs = [TokenEntryFactory() for _ in range(fake.random_int(min=1, max=10))]
        total = fake.pyint()
        wallet_service_gateway.address_tokens.return_value = (total, objs)
        wallet_service_gateway.address_flags.return_value = {
            "has_confidential_activity": True,
            "has_hidden_token_activity": False,
        }

        addr = fake.pystr()
        limit = fake.pyint()
        offset = fake.pyint()

        ws = WalletService(wallet_service_gateway)

        expected = {
            "total": total,
            "tokens": {obj.token_id: obj.to_dict() for obj in objs},
        }
        returned = ws.address_tokens(addr, limit, offset)

        assert returned["total"] == expected["total"]
        assert returned["has_confidential_activity"] is True
        assert returned["has_hidden_token_activity"] is False
        assert len(returned["tokens"]) == len(expected["tokens"])
        assert all(
            [ret == obj for ret, obj in zip(returned["tokens"], expected["tokens"])]
        )
        wallet_service_gateway.address_tokens.assert_called_once_with(
            addr, limit, offset
        )
        wallet_service_gateway.address_flags.assert_called_once_with(addr)
