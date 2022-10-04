from unittest.mock import MagicMock

from faker import Faker
from pytest import fixture

from domain.wallet_service import TokenEntry
from gateways.wallet_service_gateway import WalletServiceGateway
from tests.fixtures.wallet_service_factory import (
    TokenBalanceFactory,
    TokenEntryFactory,
    TxHistoryEntryFactory,
)

fake = Faker()


class TestWalletServiceDBClient:
    @fixture
    def db_client(self):
        return MagicMock()

    def test_init(self, db_client):
        gateway = WalletServiceGateway(db_client)
        assert gateway.db_client is db_client

    def test_address_tokens(self, db_client):
        token1 = TokenEntryFactory()
        token2 = TokenEntryFactory()
        htr_token_dict = {"token_id": "00", "name": None, "symbol": None}
        htr_token = TokenEntry.from_dict(htr_token_dict)

        total = fake.random_int()
        address = fake.pystr()
        limit = fake.pyint()
        offset = fake.pyint()

        db_client.get_address_tokens.return_value = (
            total,
            [htr_token_dict, token1.to_dict(), token2.to_dict()],
        )

        gw = WalletServiceGateway(db_client)

        total_returned, returned = gw.address_tokens(address, limit, offset)

        assert total_returned == total
        assert len(returned) == 3
        assert all(
            [ret == exp for ret, exp in zip(returned, [htr_token, token1, token2])]
        )

        assert db_client.get_address_tokens.called_once_with(address, limit, offset)

    def test_address_history(self, db_client):
        tx1 = TxHistoryEntryFactory()
        tx2 = TxHistoryEntryFactory()
        db_client.get_address_history.return_value = [
            {**tx1.to_dict(), "has_next": 1, "has_previous": 0},
            {**tx2.to_dict(), "has_next": 1, "has_previous": 0},
        ]

        gw = WalletServiceGateway(db_client)

        address = fake.pystr()
        token = fake.sha256()
        limit = fake.pyint()
        last_tx = fake.pystr()
        last_ts = fake.pyint()

        returned = gw.address_history(address, token, limit, last_tx, last_ts)

        assert len(returned['history']) == 2
        assert all([ret == exp for ret, exp in zip(returned['history'], [tx1, tx2])])

        assert db_client.get_address_history.called_once_with(
            address, token, limit, last_tx, last_ts
        )

    def test_address_balance(self, db_client):
        balance = TokenBalanceFactory()
        db_client.get_address_balance.return_value = balance.to_dict()

        gw = WalletServiceGateway(db_client)

        address = fake.pystr()
        token = fake.sha256()

        assert gw.address_balance(address, token) == balance

        assert db_client.get_address_history.called_once_with(address, token)
