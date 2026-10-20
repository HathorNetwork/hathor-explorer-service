"""A small wallet-service dataset for checking the address queries on MySQL.

Rows are written straight into the public address tables, `token`, `transaction`
and `address_balance`, the way the daemon and shielded-output recovery leave them.
"""
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sqlalchemy.engine import Connection
from sqlalchemy.sql import text

from gateways.clients.wallet_service_db_client import FULLY_SHIELDED_TOKEN_ID

HTR = "00"
BASE_TS = 1_700_000_000


def make_address(n: int) -> str:
    return f"HTestAddress{n:022d}"


def make_uid(name: str) -> str:
    return hashlib.sha256(name.encode()).hexdigest()


def make_tx_id(n: int) -> str:
    return make_uid(f"tx-{n}")


# The address with every case
ADDRESS = make_address(1)
# Has an AmountShielded-only token whose outputs were recovered
RECOVERED_ADDRESS = make_address(2)
# Has only transparent HTR activity
TRANSPARENT_ADDRESS = make_address(3)
# Never seen
UNKNOWN_ADDRESS = make_address(4)

# Transparent activity, shares txs with HTR
CUSTOM = make_uid("custom")
# Same last activity as CUSTOM, so their order falls back to token_id
CUSTOM_TIE = make_uid("custom-tie")
# Touched only through AmountShielded outputs
AMOUNT_SHIELDED = make_uid("amount-shielded")
# Older transparent activity
OLDER_1 = make_uid("older-1")
OLDER_2 = make_uid("older-2")
# Has public rows but no `token` row, like a deleted nano token
NO_TOKEN_ROW = make_uid("no-token-row")
# Has an `address_balance` row only because of a recovery
RECOVERY_ONLY = make_uid("recovery-only")

TOKENS = {
    CUSTOM: ("Custom", "CST"),
    CUSTOM_TIE: ("Custom tie", "CTIE"),
    AMOUNT_SHIELDED: ("Amount shielded", "ASH"),
    OLDER_1: ("Older one", "OLD1"),
    OLDER_2: ("Older two", "OLD2"),
    RECOVERY_ONLY: ("Recovery only", "RCV"),
}

HTR_ROWS = 2000
# Tokens no seeded address touched, so `token` is large enough for realistic plans
OTHER_TOKENS = 2000


@dataclass(frozen=True)
class HistoryRow:
    address: str
    token_id: str
    timestamp: int
    tx_id: str
    balance: int
    has_shielded: bool


@dataclass(frozen=True)
class Transaction:
    tx_id: str
    timestamp: int
    version: int
    height: Optional[int]


@dataclass(frozen=True)
class Balance:
    total_received: int
    unlocked_balance: int
    locked_balance: int
    unlocked_authorities: int
    locked_authorities: int
    # Columns the explorer must not read
    transactions: int
    unlocked_shielded_balance: int = 0
    locked_shielded_balance: int = 0
    total_shielded_received: int = 0


class Dataset:
    def __init__(self) -> None:
        self.transactions: Dict[str, Transaction] = {}
        self.history: List[HistoryRow] = []
        self.balances: Dict[Tuple[str, str], Balance] = {}
        self._build()

    def _tx(self, n: int, timestamp: int) -> str:
        tx_id = make_tx_id(n)
        self.transactions[tx_id] = Transaction(
            tx_id=tx_id,
            timestamp=timestamp,
            version=n % 4,
            height=None if n % 5 == 0 else 100 + n,
        )
        return tx_id

    def _row(
        self,
        address: str,
        token_id: str,
        n: int,
        timestamp: int,
        balance: int,
        has_shielded: bool,
    ) -> None:
        tx_id = self._tx(n, timestamp)
        self.history.append(
            HistoryRow(address, token_id, timestamp, tx_id, balance, has_shielded)
        )

    def _build(self) -> None:
        # HTR: three txs per timestamp, so pages split timestamp ties. Every tenth
        # tx is also shielded, and every twentieth is shielded only.
        for i in range(HTR_ROWS):
            has_shielded = i % 10 == 0
            balance = 0 if i % 20 == 0 else (i * 7919) % 2001 - 1000
            self._row(ADDRESS, HTR, i, BASE_TS + i // 3, balance, has_shielded)

        # Custom: in some of the HTR txs
        for i in range(0, HTR_ROWS, 80):
            self._row(ADDRESS, CUSTOM, i, BASE_TS + i // 3, 50 + i, False)
        custom_last = max(r.timestamp for r in self.history if r.token_id == CUSTOM)
        self._row(ADDRESS, CUSTOM_TIE, 1920, custom_last, 7, False)

        # FullyShielded: in some of the HTR txs, under the sentinel
        for i in range(5, HTR_ROWS, 50):
            self._row(ADDRESS, FULLY_SHIELDED_TOKEN_ID, i, BASE_TS + i // 3, 0, True)

        # AmountShielded only, in txs of their own
        for k in range(7):
            self._row(ADDRESS, AMOUNT_SHIELDED, 5000 + k, BASE_TS + 600 + k, 0, True)

        for k in range(3):
            self._row(ADDRESS, OLDER_1, 6000 + k, BASE_TS + 100 + k, 10, False)
            self._row(ADDRESS, OLDER_2, 6100 + k, BASE_TS + 50 + k, 20, False)
            self._row(ADDRESS, NO_TOKEN_ROW, 6200 + k, BASE_TS + 900 + k, 30, False)

        for k in range(2):
            self._row(
                RECOVERED_ADDRESS, AMOUNT_SHIELDED, 7000 + k, BASE_TS + k, 0, True
            )
            self._row(TRANSPARENT_ADDRESS, HTR, 8000 + k, BASE_TS + k, 100, False)

        # A voided tx keeps its `transaction` row but has no public rows
        self._tx(9000, BASE_TS + 10_000)

        self.balances = {
            (ADDRESS, HTR): Balance(
                total_received=123_456,
                unlocked_balance=1000,
                locked_balance=50,
                unlocked_authorities=0,
                locked_authorities=0,
                transactions=99_999,
                unlocked_shielded_balance=777,
                total_shielded_received=777,
            ),
            (ADDRESS, CUSTOM): Balance(
                total_received=500,
                unlocked_balance=300,
                locked_balance=0,
                unlocked_authorities=1,
                locked_authorities=2,
                transactions=26,
            ),
            # Written only by a recovery: there are no public rows for the pair
            (ADDRESS, RECOVERY_ONLY): Balance(
                total_received=0,
                unlocked_balance=0,
                locked_balance=0,
                unlocked_authorities=0,
                locked_authorities=0,
                transactions=1,
                unlocked_shielded_balance=42,
                total_shielded_received=42,
            ),
            # A recovered AmountShielded-only token: transparent columns are 0
            (RECOVERED_ADDRESS, AMOUNT_SHIELDED): Balance(
                total_received=0,
                unlocked_balance=0,
                locked_balance=0,
                unlocked_authorities=0,
                locked_authorities=0,
                transactions=2,
                unlocked_shielded_balance=10,
                total_shielded_received=10,
            ),
            (TRANSPARENT_ADDRESS, HTR): Balance(
                total_received=200,
                unlocked_balance=200,
                locked_balance=0,
                unlocked_authorities=0,
                locked_authorities=0,
                transactions=2,
            ),
        }

    # Expected values, derived from the rows

    def history_of(self, address: str, token_id: str) -> List[dict]:
        """The pair's history entries, newest first."""
        rows = [
            r for r in self.history if r.address == address and r.token_id == token_id
        ]
        rows.sort(key=lambda r: (r.timestamp, r.tx_id), reverse=True)
        return [
            {
                "tx_id": r.tx_id,
                "token_id": r.token_id,
                "balance": r.balance,
                "timestamp": r.timestamp,
                "version": self.transactions[r.tx_id].version,
                "height": self.transactions[r.tx_id].height,
            }
            for r in rows
        ]

    def public_tokens(self) -> Dict[Tuple[str, str], dict]:
        """`public_address_tokens` rows, keyed by (address, token_id)."""
        tokens: Dict[Tuple[str, str], dict] = {}
        for r in self.history:
            entry = tokens.setdefault(
                (r.address, r.token_id),
                {"transactions": 0, "shielded_transactions": 0, "last_activity": 0},
            )
            entry["transactions"] += 1
            entry["shielded_transactions"] += int(r.has_shielded)
            entry["last_activity"] = max(entry["last_activity"], r.timestamp)
        return tokens

    def custom_tokens_of(self, address: str) -> List[str]:
        """Listed custom tokens, most recently active first."""
        listed = [
            (entry["last_activity"], token_id)
            for (addr, token_id), entry in self.public_tokens().items()
            if addr == address and token_id in TOKENS
        ]
        return [token_id for _, token_id in sorted(listed, reverse=True)]

    # Writing

    def seed(self, connection: Connection) -> None:
        for table in (
            "public_address_tx_history",
            "public_address_tokens",
            "address_balance",
            "transaction",
        ):
            connection.execute(text(f"DELETE FROM `{table}`"))
        connection.execute(text("DELETE FROM token WHERE id <> '00'"))

        connection.execute(
            text("INSERT INTO token (id, name, symbol) VALUES (:id, :name, :symbol)"),
            [
                {"id": uid, "name": name, "symbol": symbol}
                for uid, (name, symbol) in TOKENS.items()
            ]
            + [
                {"id": make_uid(f"other-{n}"), "name": f"Other {n}", "symbol": "OTH"}
                for n in range(OTHER_TOKENS)
            ],
        )
        connection.execute(text("ANALYZE TABLE token"))
        connection.execute(
            text(
                "INSERT INTO transaction (tx_id, timestamp, version, height) "
                "VALUES (:tx_id, :timestamp, :version, :height)"
            ),
            [vars(tx) for tx in self.transactions.values()],
        )
        connection.execute(
            text("UPDATE transaction SET voided = TRUE WHERE tx_id = :tx_id"),
            {"tx_id": make_tx_id(9000)},
        )
        connection.execute(
            text(
                "INSERT INTO public_address_tx_history "
                "(address, token_id, timestamp, tx_id, balance, has_shielded) "
                "VALUES (:address, :token_id, :timestamp, :tx_id, :balance, :has_shielded)"
            ),
            [vars(r) for r in self.history],
        )
        connection.execute(
            text(
                "INSERT INTO public_address_tokens "
                "(address, token_id, transactions, shielded_transactions, last_activity) "
                "VALUES (:address, :token_id, :transactions, :shielded_transactions, "
                ":last_activity)"
            ),
            [
                {"address": address, "token_id": token_id, **entry}
                for (address, token_id), entry in self.public_tokens().items()
            ],
        )
        connection.execute(
            text(
                "INSERT INTO address_balance "
                "(address, token_id, total_received, unlocked_balance, locked_balance, "
                "unlocked_authorities, locked_authorities, transactions, "
                "unlocked_shielded_balance, locked_shielded_balance, "
                "total_shielded_received) "
                "VALUES (:address, :token_id, :total_received, :unlocked_balance, "
                ":locked_balance, :unlocked_authorities, :locked_authorities, "
                ":transactions, :unlocked_shielded_balance, :locked_shielded_balance, "
                ":total_shielded_received)"
            ),
            [
                {"address": address, "token_id": token_id, **vars(balance)}
                for (address, token_id), balance in self.balances.items()
            ],
        )
        connection.execute(text("ANALYZE TABLE public_address_tx_history"))
        connection.execute(text("ANALYZE TABLE public_address_tokens"))
