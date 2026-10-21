"""Checks the address queries against a real wallet-service schema.

Skipped unless WALLET_SERVICE_TEST_DB_URL points to a MySQL 8 database with the
wallet-service migrations applied. See README.md.
"""
import os
import re
from typing import Iterator, List, Optional

import pytest
from sqlalchemy.engine import Connection, Engine, create_engine
from sqlalchemy.sql import text

from common.errors import ApiError, RdsNotFoundError
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
from gateways.wallet_service_gateway import WalletServiceGateway
from tests.integration.wallet_service_db.dataset import (
    ADDRESS,
    AMOUNT_SHIELDED,
    CUSTOM,
    CUSTOM_TIE,
    HTR,
    HTR_ROWS,
    NO_TOKEN_ROW,
    RECOVERED_ADDRESS,
    RECOVERY_ONLY,
    TOKENS,
    TRANSPARENT_ADDRESS,
    UNKNOWN_ADDRESS,
    Dataset,
)
from usecases.wallet_service import WalletService

DB_URL = os.environ.get("WALLET_SERVICE_TEST_DB_URL")

pytestmark = pytest.mark.skipif(
    not DB_URL, reason="WALLET_SERVICE_TEST_DB_URL is not set"
)


@pytest.fixture(scope="module")
def dataset() -> Dataset:
    return Dataset()


@pytest.fixture(scope="module")
def engine(dataset: Dataset) -> Iterator[Engine]:
    assert DB_URL
    engine = create_engine(DB_URL)
    with engine.begin() as connection:
        dataset.seed(connection)
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def client(engine: Engine) -> WalletServiceDBClient:
    return WalletServiceDBClient(engine)


@pytest.fixture(scope="module")
def wallet_service(client: WalletServiceDBClient) -> WalletService:
    return WalletService(WalletServiceGateway(client))


def walk_history(
    client: WalletServiceDBClient,
    address: str,
    token: str,
    limit: int,
    last_tx: Optional[str] = None,
    last_ts: int = 0,
) -> Iterator[List[dict]]:
    """Yield every page, following the cursor the way the explorer does."""
    while True:
        has_next, page = client.get_address_history(
            address, token, limit, last_tx, last_ts
        )
        assert len(page) <= limit
        yield page
        if not has_next:
            return
        assert len(page) == limit
        last_tx, last_ts = page[-1]["tx_id"], page[-1]["timestamp"]


class TestHistory:
    @pytest.mark.parametrize(
        "token, limit",
        [
            (HTR, 7),
            (HTR, 10),
            (HTR, 100),
            (CUSTOM, 1),
            (CUSTOM, 5),
            (CUSTOM, 25),
            (CUSTOM, 26),
            (AMOUNT_SHIELDED, 3),
            (FULLY_SHIELDED_TOKEN_ID, 1),
            (FULLY_SHIELDED_TOKEN_ID, 10),
        ],
    )
    def test_paging_returns_the_whole_history_in_order(
        self, client, dataset, token, limit
    ):
        expected = dataset.history_of(ADDRESS, token)
        pages = list(walk_history(client, ADDRESS, token, limit))

        assert [tx for page in pages for tx in page] == expected
        assert len(pages) == max(1, -(-len(expected) // limit))

    def test_page_boundaries(self, client, dataset):
        expected = dataset.history_of(ADDRESS, CUSTOM)
        assert len(expected) == 25

        # Exactly `limit` rows left: no next page
        assert client.get_address_history(ADDRESS, CUSTOM, 25, None, 0) == (
            False,
            expected,
        )
        # One row more than `limit`
        assert client.get_address_history(ADDRESS, CUSTOM, 24, None, 0) == (
            True,
            expected[:24],
        )
        # The last row is the cursor: nothing after it
        last = expected[-1]
        assert client.get_address_history(
            ADDRESS, CUSTOM, 10, last["tx_id"], last["timestamp"]
        ) == (False, [])

    def test_deep_cursor(self, client, dataset):
        expected = dataset.history_of(ADDRESS, HTR)
        assert len(expected) == HTR_ROWS
        cursor = expected[1499]

        has_next, page = client.get_address_history(
            ADDRESS, HTR, 10, cursor["tx_id"], cursor["timestamp"]
        )

        assert has_next is True
        assert page == expected[1500:1510]

    def test_cursor_inside_a_timestamp_tie(self, client, dataset):
        expected = dataset.history_of(ADDRESS, HTR)
        # Three txs share each timestamp: pick the middle one of a group
        index = next(
            i
            for i in range(1, len(expected) - 1)
            if expected[i - 1]["timestamp"]
            == expected[i]["timestamp"]
            == expected[i + 1]["timestamp"]
        )
        cursor = expected[index]

        _, page = client.get_address_history(
            ADDRESS, HTR, 5, cursor["tx_id"], cursor["timestamp"]
        )

        assert page == expected[index + 1 : index + 6]
        assert page[0]["timestamp"] == cursor["timestamp"]

    def test_first_page_ignores_last_ts(self, client, dataset):
        expected = dataset.history_of(ADDRESS, HTR)

        assert client.get_address_history(ADDRESS, HTR, 10, None, 1) == (
            True,
            expected[:10],
        )

    def test_unknown_pair_is_empty(self, client):
        assert client.get_address_history(UNKNOWN_ADDRESS, HTR, 10, None, 0) == (
            False,
            [],
        )
        # The `address_balance` row a recovery left adds no history
        assert client.get_address_history(ADDRESS, RECOVERY_ONLY, 10, None, 0) == (
            False,
            [],
        )

    def test_shielded_only_rows_have_zero_balance(self, client, dataset):
        _, page = client.get_address_history(ADDRESS, HTR, 100, None, 0)
        shielded_only = {
            r.tx_id
            for r in dataset.history
            if r.address == ADDRESS and r.token_id == HTR and r.balance == 0
        }

        assert {tx["tx_id"] for tx in page if tx["balance"] == 0} <= shielded_only

    def test_token_history_through_the_usecase(self, wallet_service, dataset):
        expected = dataset.history_of(ADDRESS, CUSTOM)

        response = wallet_service.address_history(ADDRESS, CUSTOM, 10, None, 0)

        assert response == {"has_next": True, "history": expected[:10]}

    def test_confidential_history(self, wallet_service, dataset):
        expected = [
            {**tx, "token_id": None, "balance": None}
            for tx in dataset.history_of(ADDRESS, FULLY_SHIELDED_TOKEN_ID)
        ]
        assert len(expected) == 40

        history: List[dict] = []
        last_tx, last_ts = None, 0
        while True:
            response = wallet_service.address_confidential_history(
                ADDRESS, 15, last_tx, last_ts
            )
            history += response["history"]
            if not response["has_next"]:
                break
            last_tx = response["history"][-1]["tx_id"]
            last_ts = response["history"][-1]["timestamp"]

        assert history == expected

    def test_confidential_history_of_address_without_one(self, wallet_service):
        assert wallet_service.address_confidential_history(
            RECOVERED_ADDRESS, 10, None, 0
        ) == {"has_next": False, "history": []}

    def test_sentinel_is_not_a_token(self, wallet_service):
        with pytest.raises(ApiError, match="invalid_parameters"):
            wallet_service.address_history(
                ADDRESS, FULLY_SHIELDED_TOKEN_ID, 10, None, 0
            )


class TestTokens:
    def test_first_page_has_htr_first(self, wallet_service, dataset):
        customs = dataset.custom_tokens_of(ADDRESS)

        response = wallet_service.address_tokens(ADDRESS, 50, 0)

        assert list(response["tokens"]) == [HTR] + customs
        assert response["tokens"][HTR] == {
            "token_id": HTR,
            "name": "Hathor",
            "symbol": "HTR",
        }
        name, symbol = TOKENS[CUSTOM]
        assert response["tokens"][CUSTOM] == {
            "token_id": CUSTOM,
            "name": name,
            "symbol": symbol,
        }

    def test_listed_tokens(self, dataset):
        customs = dataset.custom_tokens_of(ADDRESS)

        # AmountShielded-only tokens are listed. The sentinel, tokens without a
        # `token` row and tokens known only through a recovery are not.
        assert AMOUNT_SHIELDED in customs
        assert FULLY_SHIELDED_TOKEN_ID not in customs
        assert NO_TOKEN_ROW not in customs
        assert RECOVERY_ONLY not in customs
        # Ties on last activity are ordered by token_id
        assert customs.index(max(CUSTOM, CUSTOM_TIE)) + 1 == customs.index(
            min(CUSTOM, CUSTOM_TIE)
        )

    def test_total_counts_htr_and_listed_tokens(self, client, dataset):
        total, _ = client.get_address_tokens(ADDRESS, 50, 0)

        assert total == 1 + len(dataset.custom_tokens_of(ADDRESS))

    @pytest.mark.parametrize("limit", [1, 2, 3, 5, 6, 50])
    def test_paging(self, client, dataset, limit):
        customs = dataset.custom_tokens_of(ADDRESS)

        _, first = client.get_address_tokens(ADDRESS, limit, 0)
        assert [t["token_id"] for t in first] == ([HTR] + customs)[:limit]

        for offset in range(1, len(customs) + 1):
            _, page = client.get_address_tokens(ADDRESS, limit, offset)
            assert [t["token_id"] for t in page] == customs[offset : offset + limit]

    def test_address_without_htr(self, client):
        total, tokens = client.get_address_tokens(RECOVERED_ADDRESS, 50, 0)

        assert total == 1
        assert [t["token_id"] for t in tokens] == [AMOUNT_SHIELDED]

    def test_unknown_address(self, wallet_service):
        assert wallet_service.address_tokens(UNKNOWN_ADDRESS, 50, 0) == {
            "total": 0,
            "tokens": {},
            "has_confidential_activity": False,
            "has_hidden_token_activity": False,
        }

    @pytest.mark.parametrize(
        "address, confidential, hidden",
        [
            (ADDRESS, True, True),
            (RECOVERED_ADDRESS, True, False),
            (TRANSPARENT_ADDRESS, False, False),
            (UNKNOWN_ADDRESS, False, False),
        ],
    )
    def test_flags(self, client, address, confidential, hidden):
        assert client.get_address_flags(address) == {
            "has_confidential_activity": confidential,
            "has_hidden_token_activity": hidden,
        }


class TestBalance:
    def test_transparent_amounts_and_public_transactions(self, wallet_service, dataset):
        stored = dataset.balances[(ADDRESS, HTR)]

        assert wallet_service.address_balance(ADDRESS, HTR) == {
            "token_id": HTR,
            "transactions": HTR_ROWS,
            "total_received": stored.total_received,
            "unlocked_balance": stored.unlocked_balance,
            "locked_balance": stored.locked_balance,
            "unlocked_authorities": stored.unlocked_authorities,
            "locked_authorities": stored.locked_authorities,
        }

    def test_authorities(self, wallet_service):
        balance = wallet_service.address_balance(ADDRESS, CUSTOM)

        assert balance["unlocked_authorities"] == 1
        assert balance["locked_authorities"] == 2
        assert balance["transactions"] == 25

    def test_amount_shielded_only_token_is_the_same_recovered_or_not(
        self, wallet_service
    ):
        zeros = {
            "token_id": AMOUNT_SHIELDED,
            "total_received": 0,
            "unlocked_balance": 0,
            "locked_balance": 0,
            "unlocked_authorities": 0,
            "locked_authorities": 0,
        }

        # No `address_balance` row
        assert wallet_service.address_balance(ADDRESS, AMOUNT_SHIELDED) == {
            **zeros,
            "transactions": 7,
        }
        # An `address_balance` row written by a recovery
        assert wallet_service.address_balance(RECOVERED_ADDRESS, AMOUNT_SHIELDED) == {
            **zeros,
            "transactions": 2,
        }

    @pytest.mark.parametrize(
        "address, token",
        [
            (ADDRESS, RECOVERY_ONLY),
            (UNKNOWN_ADDRESS, HTR),
            (RECOVERED_ADDRESS, HTR),
        ],
    )
    def test_not_found(self, wallet_service, address, token):
        with pytest.raises(RdsNotFoundError):
            wallet_service.address_balance(address, token)

    def test_values_are_ints(self, client):
        balance = client.get_address_balance(ADDRESS, AMOUNT_SHIELDED)

        assert all(type(v) is int for k, v in balance.items() if k != "token_id")


def plan_cases(dataset: Dataset) -> List[tuple]:
    """(name, query, params, rows the page should read at most)."""
    htr = dataset.history_of(ADDRESS, HTR)
    deep = htr[1499]
    return [
        (
            "history first page",
            address_history_query,
            {"address": ADDRESS, "token": HTR, "limit": 11},
            11,
        ),
        (
            "history deep page",
            address_history_after_query,
            {
                "address": ADDRESS,
                "token": HTR,
                "limit": 11,
                "last_tx": deep["tx_id"],
                "last_ts": deep["timestamp"],
            },
            11,
        ),
        (
            "confidential history first page",
            address_history_query,
            {"address": ADDRESS, "token": FULLY_SHIELDED_TOKEN_ID, "limit": 11},
            11,
        ),
        (
            "tokens list",
            address_tokens_query,
            {"address": ADDRESS, "limit": 10, "offset": 0},
            None,
        ),
        ("HTR exists", address_has_htr_query, {"address": ADDRESS}, None),
        ("token count", address_tokens_count_query, {"address": ADDRESS}, None),
        ("flags", address_flags_query, {"address": ADDRESS}, None),
        ("balance", address_balance_query, {"address": ADDRESS, "token": HTR}, None),
    ]


def explain_analyze(connection: Connection, query: str, params: dict) -> str:
    rows = connection.execute(text("EXPLAIN ANALYZE " + query), **params)
    return "\n".join(row[0] for row in rows)


class TestPlans:
    @pytest.mark.parametrize("case", range(8))
    def test_plan_reads_only_the_address_rows(self, engine, dataset, case):
        name, query, params, max_rows = plan_cases(dataset)[case]
        with engine.connect() as connection:
            plan = explain_analyze(connection, query, params)

        # The public tables are always read through an index of the address
        assert not re.search(r"Table scan on (p|public_\w+)\b", plan), plan
        # `token` is only looked up by id
        assert not re.search(r"(Table|index) scan on token\b", plan), plan
        # Only the materialized history page may be sorted
        sorts = re.findall(r"Sort: (\S+)", plan) + re.findall(r"filesort", plan)
        assert all(sort.startswith("`page`") for sort in sorts), plan

        if max_rows is not None:
            # The rows actually read from the history's primary key
            history_scan = re.search(
                r"on public_address_tx_history using PRIMARY[^\n]*"
                r"\(actual time=[\d.]+\.\.[\d.]+ rows=(\d+)",
                plan,
            )
            assert history_scan, plan
            assert int(history_scan.group(1)) <= max_rows, plan
