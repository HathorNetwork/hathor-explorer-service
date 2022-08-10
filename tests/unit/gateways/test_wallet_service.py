from unittest.mock import MagicMock

from faker import Faker
from pytest import fixture

from domain.wallet_service import TokenEntry
from gateways.wallet_service_gateway import WalletServiceGateway
from tests.fixtures.wallet_service_factory import TokenBalanceFactory, TokenEntryFactory, TxHistoryEntryFactory

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
        htr_token_dict = {'token_id': '00', 'name': None, 'symbol': None}
        htr_token = TokenEntry.from_dict(htr_token_dict)

        total = fake.random_int()
        address = fake.pystr()
        limit = fake.pyint()
        offset = fake.pyint()

        # we only check the first entry for the `total` value since all should contain the same `total`
        t1dict = token1.to_dict()
        t1dict['total'] = total

        db_client.get_address_tokens.return_value = [t1dict, token2.to_dict(), htr_token_dict]

        gw = WalletServiceGateway(db_client)

        total_returned, returned = gw.address_tokens(address, limit, offset)

        assert total_returned == total
        assert len(returned) == 3
        assert all([ret == exp for ret, exp in zip(returned, [token1, token2, htr_token])])

        assert db_client.get_address_tokens.called_once_with(address, limit, offset)

    def test_address_history(self, db_client):
        tx1 = TxHistoryEntryFactory()
        tx2 = TxHistoryEntryFactory()
        db_client.get_address_history.return_value = [tx1.to_dict(), tx2.to_dict()]

        gw = WalletServiceGateway(db_client)

        address = fake.pystr()
        token = fake.sha256()
        limit = fake.pyint()
        offset = fake.pyint()

        returned = gw.address_history(address, token, limit, offset)

        assert len(returned) == 2
        assert all([ret == exp for ret, exp in zip(returned, [tx1, tx2])])

        assert db_client.get_address_history.called_once_with(address, token, limit, offset)

    def test_address_balance(self, db_client):
        balance = TokenBalanceFactory()
        db_client.get_address_balance.return_value = balance.to_dict()

        gw = WalletServiceGateway(db_client)

        address = fake.pystr()
        token = fake.sha256()

        assert gw.address_balance(address, token) == balance

        assert db_client.get_address_history.called_once_with(address, token)
