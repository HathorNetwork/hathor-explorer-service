from unittest.mock import MagicMock

from faker import Faker
from pytest import fixture

from domain.wallet_service import TokenEntry
from gateways.clients.wallet_service_db_client import FULLY_SHIELDED_TOKEN_ID
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

        db_client.get_address_tokens.assert_called_once_with(address, limit, offset)

    def test_address_history(self, db_client):
        tx1 = TxHistoryEntryFactory()
        tx2 = TxHistoryEntryFactory()
        db_client.get_address_history.return_value = (
            True,
            [tx1.to_dict(), tx2.to_dict()],
        )

        gw = WalletServiceGateway(db_client)

        address = fake.pystr()
        token = fake.sha256()
        limit = fake.pyint()
        last_tx = fake.sha256()
        last_ts = fake.pyint()

        returned = gw.address_history(address, token, limit, last_tx, last_ts)

        assert returned["has_next"] is True
        assert returned["history"] == [tx1.to_dict(), tx2.to_dict()]

        db_client.get_address_history.assert_called_once_with(
            address, token, limit, last_tx, last_ts
        )

    def test_address_history_empty(self, db_client):
        db_client.get_address_history.return_value = (False, [])

        gw = WalletServiceGateway(db_client)

        assert gw.address_history(fake.pystr(), fake.sha256(), 10, None, 0) == {
            "has_next": False,
            "history": [],
        }

    def test_address_confidential_history(self, db_client):
        tx1 = TxHistoryEntryFactory(token_id=FULLY_SHIELDED_TOKEN_ID, balance=0)
        tx2 = TxHistoryEntryFactory(token_id=FULLY_SHIELDED_TOKEN_ID, balance=0)
        db_client.get_address_history.return_value = (
            False,
            [tx1.to_dict(), tx2.to_dict()],
        )

        gw = WalletServiceGateway(db_client)

        address = fake.pystr()
        limit = fake.pyint()
        last_tx = fake.sha256()
        last_ts = fake.pyint()

        returned = gw.address_confidential_history(address, limit, last_tx, last_ts)

        assert returned["has_next"] is False
        # The sentinel and the stored balance are not returned
        assert returned["history"] == [
            {**tx.to_dict(), "token_id": None, "balance": None} for tx in (tx1, tx2)
        ]

        db_client.get_address_history.assert_called_once_with(
            address, FULLY_SHIELDED_TOKEN_ID, limit, last_tx, last_ts
        )

    def test_is_reserved_token(self, db_client):
        gw = WalletServiceGateway(db_client)

        assert gw.is_reserved_token(FULLY_SHIELDED_TOKEN_ID)
        assert not gw.is_reserved_token("00")
        assert not gw.is_reserved_token(fake.sha256())

    def test_address_flags(self, db_client):
        flags = {"has_confidential_activity": True, "has_hidden_token_activity": False}
        db_client.get_address_flags.return_value = flags

        gw = WalletServiceGateway(db_client)

        address = fake.pystr()

        assert gw.address_flags(address) == flags
        db_client.get_address_flags.assert_called_once_with(address)

    def test_address_balance(self, db_client):
        balance = TokenBalanceFactory()
        db_client.get_address_balance.return_value = balance.to_dict()

        gw = WalletServiceGateway(db_client)

        address = fake.pystr()
        token = fake.sha256()

        assert gw.address_balance(address, token) == balance

        db_client.get_address_balance.assert_called_once_with(address, token)
