from unittest.mock import MagicMock

from faker import Faker
from pytest import fixture

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
        return MagicMock()

    def test_address_balance(self, wallet_service_gateway):
        obj = TokenBalanceFactory()
        wallet_service_gateway.address_balance.return_value = obj

        addr = fake.pystr()
        token = fake.sha256()

        ws = WalletService(wallet_service_gateway)

        assert ws.address_balance(addr, token) == obj.to_dict()
        wallet_service_gateway.address_balance.assert_called_once_with(addr, token)

    def test_address_history(self, wallet_service_gateway):
        objs = [TxHistoryEntryFactory() for _ in range(fake.random_int(min=1, max=10))]
        wallet_service_gateway.address_history.return_value = objs

        addr = fake.pystr()
        token = fake.sha256()
        limit = fake.pyint()
        offset = fake.pyint()

        ws = WalletService(wallet_service_gateway)

        expected = [obj.to_dict() for obj in objs]
        returned = ws.address_history(addr, token, limit, offset)

        assert len(returned) == len(expected)
        assert all([ret == obj for ret, obj in zip(returned, expected)])
        wallet_service_gateway.address_history.assert_called_once_with(
            addr, token, limit, offset
        )

    def test_address_tokens(self, wallet_service_gateway):
        objs = [TokenEntryFactory() for _ in range(fake.random_int(min=1, max=10))]
        total = fake.pyint()
        wallet_service_gateway.address_tokens.return_value = (total, objs)

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
        assert len(returned["tokens"]) == len(expected["tokens"])
        assert all(
            [ret == obj for ret, obj in zip(returned["tokens"], expected["tokens"])]
        )
        wallet_service_gateway.address_tokens.assert_called_once_with(
            addr, limit, offset
        )
