from unittest.mock import MagicMock

from faker import Faker
from pytest import fixture

from tests.fixtures.wallet_service_factory import TokenBalanceFactory, TokenEntryFactory, TxHistoryEntryFactory
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
        count = fake.pyint()
        skip = fake.pyint()

        ws = WalletService(wallet_service_gateway)

        expected = [obj.to_dict() for obj in objs]
        returned = ws.address_history(addr, token, count, skip)

        assert len(returned) == len(expected)
        assert all([ret == obj for ret, obj in zip(returned, expected)])
        wallet_service_gateway.address_history.assert_called_once_with(addr, token, count, skip)

    def test_address_tokens(self, wallet_service_gateway):
        objs = [TokenEntryFactory() for _ in range(fake.random_int(min=1, max=10))]
        wallet_service_gateway.address_tokens.return_value = objs

        addr = fake.pystr()

        ws = WalletService(wallet_service_gateway)

        expected = [obj.to_dict() for obj in objs]
        returned = ws.address_tokens(addr)

        assert len(returned) == len(expected)
        assert all([ret == obj for ret, obj in zip(returned, expected)])
        wallet_service_gateway.address_tokens.assert_called_once_with(addr)
