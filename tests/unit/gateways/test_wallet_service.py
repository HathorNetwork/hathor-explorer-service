from unittest.mock import MagicMock

from pytest import fixture

from domain.wallet_service import TokenEntry
from gateways.wallet_service_gateway import WalletServiceGateway
from tests.fixtures.wallet_service_factory import TokenBalanceFactory, TokenEntryFactory, TxHistoryEntryFactory


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

        db_client.get_address_tokens.return_value = [token1.to_dict(), token2.to_dict(), htr_token_dict]

        gw = WalletServiceGateway(db_client)

        returned = gw.address_tokens('H1')

        assert len(returned) == 3
        assert all([ret == exp for ret, exp in zip(returned, [token1, token2, htr_token])])

        assert db_client.get_address_tokens.called_once_with('H1')

    def test_address_history(self, db_client):
        tx1 = TxHistoryEntryFactory()
        tx2 = TxHistoryEntryFactory()
        db_client.get_address_history.return_value = [tx1.to_dict(), tx2.to_dict()]

        gw = WalletServiceGateway(db_client)

        returned = gw.address_history('H2', 'TK2', 10, 20)

        assert len(returned) == 2
        assert all([ret == exp for ret, exp in zip(returned, [tx1, tx2])])

        assert db_client.get_address_history.called_once_with('H2', 'TK2', 10, 20)

    def test_address_balance(self, db_client):
        balance = TokenBalanceFactory()
        db_client.get_address_balance.return_value = balance.to_dict()

        gw = WalletServiceGateway(db_client)

        assert gw.address_balance('H3', 'TK3') == balance

        assert db_client.get_address_history.called_once_with('H3', 'TK3')
