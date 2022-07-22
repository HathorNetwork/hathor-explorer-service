from unittest.mock import ANY, MagicMock, patch

import pytest
from pytest import fixture
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from common.errors import RdsError, RdsNotFoundError
from gateways.clients.wallet_service_db_client import (
    WalletServiceDBClient,
    address_balance_query,
    address_history_query,
    address_tokens_query,
)


class TestWalletServiceDBClient:

    @fixture
    def connection(self):
        return MagicMock()

    @fixture
    def engine(self, connection):
        engine = MagicMock()
        conn_manager = MagicMock()
        conn_manager.__enter__.return_value = connection
        engine.connect.return_value = conn_manager
        return engine

    def row_from_dict(self, dikt):
        row = MagicMock()
        row._asdict.return_value = dikt
        return row

    def test_init(self, engine, connection):
        client = WalletServiceDBClient(engine)
        assert client.engine is engine
        with client.engine.connect() as conn:
            assert conn is connection

    def test_get_address_tokens(self, engine, connection):
        cursor = [
            self.row_from_dict('dict_value_1'),
            self.row_from_dict('dict_value_2'),
        ]
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        # Should return the dict value of the request
        assert client.get_address_tokens('H1') == ['dict_value_1', 'dict_value_2']

        # Should pass the expected args to execute
        print(connection.execute.call_args)
        connection.execute.assert_called_once_with(ANY, address='H1')
        # Should use the correct query for this method
        assert connection.execute.call_args[0][0].text == address_tokens_query

    def test_get_address_history(self, engine, connection):
        cursor = [
            self.row_from_dict('dict_value_1'),
            self.row_from_dict('dict_value_2'),
        ]
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        # Should return the dict value of the request
        assert client.get_address_history('H3', 'TK3', 27, 105) == ['dict_value_1', 'dict_value_2']

        # Should pass the expected args to execute
        connection.execute.assert_called_once_with(ANY, address='H3', token='TK3', count=27, skip=105)
        # Should use the correct query for this method
        assert connection.execute.call_args[0][0].text == address_history_query

    @patch('sqlalchemy.sql.text', MagicMock(return_value='text_query'))
    def test_get_address_balance(self, engine, connection):
        cursor = MagicMock()
        cursor.one.return_value = self.row_from_dict('dict_value')
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        # Should return the dict value of the request
        assert client.get_address_balance('H2', 'TK2') == 'dict_value'

        # Should pass the expected args to execute
        connection.execute.assert_called_once_with(ANY, address='H2', token='TK2')
        # Should use the correct query for this method
        assert connection.execute.call_args[0][0].text == address_balance_query

    def test_get_address_balance_errors(self, engine, connection):
        cursor = MagicMock()
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        cursor.one.side_effect = Exception('Boom!')
        with pytest.raises(Exception):
            client.get_address_balance('H123', 'TK123')

        cursor.one.side_effect = MultipleResultsFound('Boom!')
        with pytest.raises(RdsError):
            client.get_address_balance('H123', 'TK123')

        cursor.one.side_effect = NoResultFound('Boom!')
        with pytest.raises(RdsNotFoundError):
            client.get_address_balance('H123', 'TK123')
