from unittest.mock import ANY, MagicMock, call

import pytest
from faker import Faker
from pytest import fixture
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from common.errors import RdsError, RdsNotFoundError
from gateways.clients.wallet_service_db_client import (
    WalletServiceDBClient,
    address_balance_query,
    address_has_htr_query,
    address_history_query,
    address_tokens_count_query,
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

    def test_get_address_history(self, engine, connection):
        cursor = [
            self.row_from_dict("dict_value_1"),
            self.row_from_dict("dict_value_2"),
        ]
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        address = "H" + fake.pystr()
        token = fake.sha256()
        limit = fake.random_int()
        last_ts = fake.random_int()
        last_tx = fake.pystr()

        # Should return the dict value of the request
        assert client.get_address_history(address, token, limit, last_tx, last_ts) == [
            "dict_value_1",
            "dict_value_2",
        ]

        # Should pass the expected args to execute
        connection.execute.assert_called_once_with(
            ANY,
            address=address,
            token=token,
            limit=limit,
            last_tx=last_tx,
            last_ts=last_ts,
        )
        # Should use the correct query for this method
        assert connection.execute.call_args[0][0].text == address_history_query

    def test_get_address_balance(self, engine, connection):
        cursor = MagicMock()
        cursor.one.return_value = self.row_from_dict("dict_value")
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        address = "H" + fake.pystr()
        token = fake.sha256()

        # Should return the dict value of the request
        assert client.get_address_balance(address, token) == "dict_value"

        # Should pass the expected args to execute
        connection.execute.assert_called_once_with(ANY, address=address, token=token)
        # Should use the correct query for this method
        assert connection.execute.call_args[0][0].text == address_balance_query

    def test_get_address_balance_errors(self, engine, connection):
        cursor = MagicMock()
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        address = "H" + fake.pystr()
        token = fake.sha256()

        cursor.one.side_effect = Exception("Boom!")
        with pytest.raises(Exception):
            client.get_address_balance(address, token)

        cursor.one.side_effect = MultipleResultsFound("Boom!")
        with pytest.raises(RdsError):
            client.get_address_balance(address, token)

        cursor.one.side_effect = NoResultFound("Boom!")
        with pytest.raises(RdsNotFoundError):
            client.get_address_balance(address, token)

    def test_get_address_tokens(self, engine, connection):
        fake_total = fake.random_int()

        def cursor_func(q, **kwargs):
            if q.text == address_tokens_count_query:
                cursor = MagicMock()
                cursor.one.return_value = {"total": fake_total}
                return cursor
            elif q.text == address_tokens_query:
                return [
                    self.row_from_dict("dict_value_1"),
                    self.row_from_dict("dict_value_2"),
                ]
            else:
                raise Exception("Running unexpected query")

        connection.execute.side_effect = cursor_func

        client = WalletServiceDBClient(engine)

        address = fake.pystr()
        limit = fake.random_int()
        offset = fake.random_int(min=1)

        # Should return the dict value of the request
        total, tokens = client.get_address_tokens(address, limit, offset)
        assert total == fake_total
        # Should return the dict value of the request
        assert tokens == ["dict_value_1", "dict_value_2"]

        # Should pass the expected args to execute
        print(connection.execute.call_args_list)
        assert connection.execute.call_count == 2
        connection.execute.assert_has_calls(
            [
                call(ANY, address=address),
                call(ANY, address=address, limit=limit, offset=offset),
            ]
        )
        # Should use the correct query for this method
        assert (
            connection.execute.call_args_list[0][0][0].text
            == address_tokens_count_query
        )
        assert connection.execute.call_args_list[1][0][0].text == address_tokens_query

    def test_get_address_tokens_with_htr(self, engine, connection):
        fake_total = fake.random_int()

        def cursor_func(q, **kwargs):
            if q.text == address_has_htr_query:
                cursor = MagicMock()
                cursor.one_or_none.return_value = self.row_from_dict("htr_dict_value")
                return cursor
            elif q.text == address_tokens_count_query:
                cursor = MagicMock()
                cursor.one.return_value = {"total": fake_total}
                return cursor
            elif q.text == address_tokens_query:
                return [
                    self.row_from_dict("dict_value_1"),
                    self.row_from_dict("dict_value_2"),
                ]
            else:
                raise Exception("Running unexpected query")

        connection.execute.side_effect = cursor_func

        client = WalletServiceDBClient(engine)

        address = fake.pystr()
        limit = fake.random_int()

        # Should return the dict value of the request
        total, tokens = client.get_address_tokens(address, limit, 0)
        assert total == fake_total
        # Should return the dict value of the request
        assert tokens == ["htr_dict_value", "dict_value_1", "dict_value_2"]

        # Should pass the expected args to execute
        print(connection.execute.call_args_list)
        assert connection.execute.call_count == 3
        connection.execute.assert_has_calls(
            [
                call(ANY, address=address),
                call(ANY, address=address),
                call(ANY, address=address, limit=limit - 1, offset=0),
            ]
        )
        # Should use the correct queries for the method
        assert (
            connection.execute.call_args_list[0][0][0].text
            == address_tokens_count_query
        )
        assert connection.execute.call_args_list[1][0][0].text == address_has_htr_query
        assert connection.execute.call_args_list[2][0][0].text == address_tokens_query

    def test_get_address_tokens_without_htr(self, engine, connection):
        fake_total = fake.random_int()

        def cursor_func(q, **kwargs):
            if q.text == address_has_htr_query:
                cursor = MagicMock()
                cursor.one_or_none.return_value = None
                return cursor
            elif q.text == address_tokens_count_query:
                cursor = MagicMock()
                cursor.one.return_value = {"total": fake_total}
                return cursor
            elif q.text == address_tokens_query:
                return [
                    self.row_from_dict("dict_value_1"),
                    self.row_from_dict("dict_value_2"),
                ]
            else:
                raise Exception("Running unexpected query")

        connection.execute.side_effect = cursor_func

        client = WalletServiceDBClient(engine)

        address = fake.pystr()
        limit = fake.random_int()

        total, tokens = client.get_address_tokens(address, limit, 0)
        assert total == fake_total
        # Should return the dict value of the request
        assert tokens == ["dict_value_1", "dict_value_2"]

        # Should pass the expected args to execute
        print(connection.execute.call_args_list)
        assert connection.execute.call_count == 3
        connection.execute.assert_has_calls(
            [
                call(ANY, address=address),
                call(ANY, address=address),
                call(ANY, address=address, limit=limit, offset=0),
            ]
        )
        # Should use the correct queries for the method
        assert (
            connection.execute.call_args_list[0][0][0].text
            == address_tokens_count_query
        )
        assert connection.execute.call_args_list[1][0][0].text == address_has_htr_query
        assert connection.execute.call_args_list[2][0][0].text == address_tokens_query
