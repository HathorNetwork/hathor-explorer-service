import re
from unittest.mock import ANY, MagicMock, call

import pytest
from faker import Faker
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from common.errors import RdsError, RdsNotFoundError
from gateways.clients import wallet_service_db_client
from gateways.clients.wallet_service_db_client import (
    FULLY_SHIELDED_TOKEN_ID,
    WalletServiceDBClient,
    address_balance_query,
    address_flags_query,
    address_has_htr_query,
    address_history_after_query,
    address_history_query,
    address_tokens_count_query,
    address_tokens_query,
)

fake = Faker()

# Tables whose rows and values never depend on shielded-output recovery
ALLOWED_TABLES = {
    "public_address_tx_history",
    "public_address_tokens",
    "token",
    "transaction",
    "address_balance",
}
# Columns of `address_balance` that recovery never writes
ADDRESS_BALANCE_ALLOWED_COLUMNS = {
    "address",
    "token_id",
    "total_received",
    "unlocked_balance",
    "locked_balance",
    "unlocked_authorities",
    "locked_authorities",
}
# Columns of `address_balance` that recovery writes, or that reveal when it ran
ADDRESS_BALANCE_FORBIDDEN_COLUMNS = {
    "transactions",
    "timelock_expires",
    "created_at",
    "updated_at",
}
# Identifiers mentioning `shielded` that belong to the public address tables
ALLOWED_SHIELDED_IDENTIFIERS = {
    "shielded_transactions",
    "has_shielded",
    FULLY_SHIELDED_TOKEN_ID,
}


def client_queries() -> dict:
    """Every query string the client module defines."""
    return {
        name: value
        for name, value in vars(wallet_service_db_client).items()
        if name.endswith("_query") and isinstance(value, str)
    }


class TestQueriesReadOnlyPublicData:
    def test_finds_every_query(self):
        assert set(client_queries()) == {
            "address_balance_query",
            "address_history_query",
            "address_history_after_query",
            "address_tokens_query",
            "address_has_htr_query",
            "address_tokens_count_query",
            "address_flags_query",
            "ping_query",
        }

    @pytest.mark.parametrize("name", sorted(client_queries()))
    def test_reads_only_allowed_tables(self, name):
        query = client_queries()[name]
        tables = set(re.findall(r"\b(?:FROM|JOIN)\s+(\w+)", query, re.IGNORECASE))
        assert tables <= ALLOWED_TABLES

        for forbidden in ("tx_output", "address_tx_history", "recovery_state"):
            # `\b` does not match inside `public_address_tx_history`
            assert not re.search(rf"\b{forbidden}\b", query)

    @pytest.mark.parametrize("name", sorted(client_queries()))
    def test_reads_no_shielded_column(self, name):
        query = client_queries()[name]
        identifiers = set(re.findall(r"\w*shielded\w*", query, re.IGNORECASE))
        assert identifiers <= ALLOWED_SHIELDED_IDENTIFIERS

    @pytest.mark.parametrize("name", sorted(client_queries()))
    def test_reads_only_transparent_address_balance_columns(self, name):
        query = client_queries()[name]
        if not re.search(r"\baddress_balance\b", query):
            return

        # `address_balance` must be aliased, and only its allowed columns read
        aliases = re.findall(r"\baddress_balance\s+(?:AS\s+)?(\w+)", query)
        assert len(aliases) == 1 and aliases[0].upper() not in ("ON", "WHERE")
        alias = aliases[0]
        columns = set(re.findall(rf"\b{alias}\.(\w+)", query))
        assert columns <= ADDRESS_BALANCE_ALLOWED_COLUMNS
        assert not re.search(r"\baddress_balance\.", query)

        # An unqualified forbidden column would resolve to `address_balance`
        for column in ADDRESS_BALANCE_FORBIDDEN_COLUMNS:
            assert not re.search(rf"(?<![.\w])(?<!AS ){column}\b", query)


class TestWalletServiceDBClient:
    @pytest.fixture
    def connection(self):
        return MagicMock()

    @pytest.fixture
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
        limit = fake.random_int(min=2)
        last_ts = fake.random_int()

        # Should return the dict value of the request
        assert client.get_address_history(address, token, limit, None, last_ts) == (
            False,
            ["dict_value_1", "dict_value_2"],
        )

        # Should fetch one row more than the page, without a cursor
        connection.execute.assert_called_once_with(
            ANY,
            address=address,
            token=token,
            limit=limit + 1,
        )
        # Should use the first page query
        assert connection.execute.call_args[0][0].text == address_history_query

    def test_get_address_history_after_cursor(self, engine, connection):
        connection.execute.return_value = [self.row_from_dict("dict_value_1")]

        client = WalletServiceDBClient(engine)

        address = "H" + fake.pystr()
        token = fake.sha256()
        limit = fake.random_int(min=1)
        last_ts = fake.random_int()
        last_tx = fake.sha256()

        assert client.get_address_history(address, token, limit, last_tx, last_ts) == (
            False,
            ["dict_value_1"],
        )

        connection.execute.assert_called_once_with(
            ANY,
            address=address,
            token=token,
            limit=limit + 1,
            last_tx=last_tx,
            last_ts=last_ts,
        )
        # Should use the cursor query
        assert connection.execute.call_args[0][0].text == address_history_after_query

    @pytest.mark.parametrize(
        "rows, has_next, page_size",
        [(0, False, 0), (4, False, 4), (5, False, 5), (6, True, 5)],
    )
    def test_get_address_history_has_next(
        self, engine, connection, rows, has_next, page_size
    ):
        limit = 5
        connection.execute.return_value = [
            self.row_from_dict(f"dict_value_{i}") for i in range(rows)
        ]

        client = WalletServiceDBClient(engine)

        returned_has_next, history = client.get_address_history(
            "H" + fake.pystr(), fake.sha256(), limit, None, 0
        )

        assert returned_has_next is has_next
        # Should drop the extra row
        assert history == [f"dict_value_{i}" for i in range(page_size)]

    def test_history_queries(self):
        cursor = "(timestamp < :last_ts OR (timestamp = :last_ts AND tx_id < :last_tx))"
        # The cursor is expanded so MySQL can range-scan the primary key
        assert cursor not in address_history_query
        assert cursor in address_history_after_query
        assert ":last_tx" not in address_history_query
        # The two variants differ only by the cursor
        assert (
            re.sub(r"\n\s+AND " + re.escape(cursor), "", address_history_after_query)
            == address_history_query
        )

    def test_get_address_flags(self, engine, connection):
        cursor = MagicMock()
        cursor.one.return_value = self.row_from_dict(
            {"has_confidential_activity": 1, "has_hidden_token_activity": 0}
        )
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        address = "H" + fake.pystr()

        assert client.get_address_flags(address) == {
            "has_confidential_activity": True,
            "has_hidden_token_activity": False,
        }

        connection.execute.assert_called_once_with(ANY, address=address)
        assert connection.execute.call_args[0][0].text == address_flags_query
        cursor.close.assert_called_once()

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

    def test_ping(self, engine, connection):
        class mockRow(list):
            def _asdict(self):
                return {}

        cursor = MagicMock()
        result = mockRow()
        result.append(1)
        cursor.one.return_value = result
        connection.execute.return_value = cursor

        client = WalletServiceDBClient(engine)

        assert client.ping() == (True, {})

        # Should pass the expected args to execute
        connection.execute.assert_called_once()
        # Should use the correct query for this method
        assert connection.execute.call_args[0][0].text == "SELECT 1"
