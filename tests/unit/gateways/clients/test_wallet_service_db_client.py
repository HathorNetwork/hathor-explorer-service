from unittest.mock import ANY, MagicMock

import pytest
from faker import Faker
from pytest import fixture
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from common.errors import RdsError, RdsNotFoundError
from gateways.clients.wallet_service_db_client import (
    WalletServiceDBClient,
    address_balance_query,
    address_history_query,
    address_tokens_query,
)

fake = Faker()


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

        address = 'H' + fake.pystr()
        limit = fake.pyint()
        offset = fake.pyint()

        # Should return the dict value of the request
        assert client.get_address_tokens(address, limit, offset) == ['dict_value_1', 'dict_value_2']

        # Should pass the expected args to execute
        print(connection.execute.call_args)
        connection.execute.assert_called_once_with(ANY, address=address, limit=limit, offset=offset)
        # Should use the correct query for this method
        assert connection.execute.call_args[0][0].text == address_tokens_query

    def test_get_address_history(self, engine, connection):
        cursor = [
            self.row_from_dict('dict_value_1'),
            self.row_from_dict('dict_value_2'),
        ]
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        address = 'H' + fake.pystr()
        token = fake.sha256()
        limit = fake.pyint()
        offset = fake.pyint()

        # Should return the dict value of the request
        assert client.get_address_history(address, token, limit, offset) == ['dict_value_1', 'dict_value_2']

        # Should pass the expected args to execute
        connection.execute.assert_called_once_with(ANY, address=address, token=token, limit=limit, offset=offset)
        # Should use the correct query for this method
        assert connection.execute.call_args[0][0].text == address_history_query

    def test_get_address_balance(self, engine, connection):
        cursor = MagicMock()
        cursor.one.return_value = self.row_from_dict('dict_value')
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        address = 'H' + fake.pystr()
        token = fake.sha256()

        # Should return the dict value of the request
        assert client.get_address_balance(address, token) == 'dict_value'

        # Should pass the expected args to execute
        connection.execute.assert_called_once_with(ANY, address=address, token=token)
        # Should use the correct query for this method
        assert connection.execute.call_args[0][0].text == address_balance_query

    def test_get_address_balance_errors(self, engine, connection):
        cursor = MagicMock()
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        address = 'H' + fake.pystr()
        token = fake.sha256()

        cursor.one.side_effect = Exception('Boom!')
        with pytest.raises(Exception):
            client.get_address_balance(address, token)

        cursor.one.side_effect = MultipleResultsFound('Boom!')
        with pytest.raises(RdsError):
            client.get_address_balance(address, token)

        cursor.one.side_effect = NoResultFound('Boom!')
        with pytest.raises(RdsNotFoundError):
            client.get_address_balance(address, token)
