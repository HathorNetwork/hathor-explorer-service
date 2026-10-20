from typing import TYPE_CHECKING, List, Optional, Tuple

from sqlalchemy.engine import URL, create_engine
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

from common.configuration import (
    ENVIRONMENT,
    WALLET_SERVICE_DB_HOST,
    WALLET_SERVICE_DB_NAME,
    WALLET_SERVICE_DB_PASSWORD,
    WALLET_SERVICE_DB_USERNAME,
)
from common.errors import RdsError, RdsNotFoundError

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine, Row


# FullyShielded involvement is recorded in the public address tables under this
# token_id, never under a real token. It is not hex, so it never matches a `token`
# row. The wallet-service daemon uses the same literal.
FULLY_SHIELDED_TOKEN_ID = "fully_shielded"

# The address queries read only the public address tables, `token`, `transaction`
# and the transparent columns of `address_balance`. Shielded-output recovery writes
# `tx_output`, `address_tx_history` and the rest of `address_balance`, so reading
# those would reveal which outputs were recovered.

# A pair with only AmountShielded involvement may have no `address_balance` row,
# so its amounts are 0. COALESCE with a literal returns a DECIMAL, hence the CAST.
address_balance_query: str = """\
   SELECT p.token_id AS token_id,
          p.transactions AS transactions,
          CAST(COALESCE(b.total_received, 0) AS UNSIGNED) AS total_received,
          CAST(COALESCE(b.unlocked_balance, 0) AS UNSIGNED) AS unlocked_balance,
          CAST(COALESCE(b.locked_balance, 0) AS UNSIGNED) AS locked_balance,
          CAST(COALESCE(b.unlocked_authorities, 0) AS UNSIGNED) AS unlocked_authorities,
          CAST(COALESCE(b.locked_authorities, 0) AS UNSIGNED) AS locked_authorities
     FROM public_address_tokens p
LEFT JOIN address_balance b
       ON b.address = p.address AND b.token_id = p.token_id
    WHERE p.address = :address AND p.token_id = :token"""

# The page is selected from the history's primary key first, then joined with
# `transaction`. The cursor is written as an expanded OR because MySQL does not
# range-optimize a row-constructor comparison.
_address_history_query_template = """\
    SELECT page.tx_id AS tx_id,
           page.token_id AS token_id,
           page.balance AS balance,
           page.timestamp AS timestamp,
           transaction.version AS version,
           transaction.height AS height
      FROM (
             SELECT tx_id, token_id, balance, timestamp
               FROM public_address_tx_history
              WHERE address = :address
                AND token_id = :token{cursor}
           ORDER BY timestamp DESC, tx_id DESC
              LIMIT :limit
           ) page
INNER JOIN transaction ON transaction.tx_id = page.tx_id
  ORDER BY page.timestamp DESC, page.tx_id DESC"""

address_history_query: str = _address_history_query_template.format(cursor="")

address_history_after_query: str = _address_history_query_template.format(
    cursor="""
                AND (timestamp < :last_ts OR (timestamp = :last_ts AND tx_id < :last_tx))"""
)

address_tokens_query: str = """\
    SELECT p.token_id AS token_id,
           token.name AS name,
           token.symbol AS symbol
      FROM public_address_tokens p
INNER JOIN token ON token.id = p.token_id
     WHERE p.address = :address AND p.token_id <> '00'
  ORDER BY p.last_activity DESC, p.token_id DESC
     LIMIT :limit OFFSET :offset"""

address_has_htr_query: str = """\
SELECT '00' AS token_id, 'Hathor' AS name, 'HTR' AS symbol
  FROM public_address_tokens
 WHERE address = :address AND token_id = '00'"""

address_tokens_count_query: str = """\
    SELECT COUNT(*) AS total
      FROM public_address_tokens p
INNER JOIN token ON token.id = p.token_id
     WHERE p.address = :address"""

address_flags_query: str = f"""\
SELECT EXISTS (
         SELECT 1 FROM public_address_tokens
          WHERE address = :address AND shielded_transactions > 0
       ) AS has_confidential_activity,
       EXISTS (
         SELECT 1 FROM public_address_tokens
          WHERE address = :address AND token_id = '{FULLY_SHIELDED_TOKEN_ID}'
       ) AS has_hidden_token_activity"""

ping_query: str = "SELECT 1"


def get_engine():
    """Returns the engine for connecting with the wallet service database.

    NullPool is used to disable connection pooling
    making each connect/disconnect actually grab a connection and release the connection.
    """
    wallet_service_url = URL(
        "mysql+pymysql",
        username=WALLET_SERVICE_DB_USERNAME,
        password=WALLET_SERVICE_DB_PASSWORD,
        host=WALLET_SERVICE_DB_HOST,
        port=3306,
        database=WALLET_SERVICE_DB_NAME,
    )

    return create_engine(
        wallet_service_url, poolclass=NullPool, echo=ENVIRONMENT.is_dev
    )


class WalletServiceDBClient:
    def __init__(self, engine: Optional["Engine"] = None):
        self.engine = engine or get_engine()

    def get_address_balance(self, address: str, token: str) -> dict:
        """Fetch the token balance of an address."""
        result: "Row"
        with self.engine.connect() as connection:
            cursor = connection.execute(
                text(address_balance_query), address=address, token=token
            )
            try:
                result = cursor.one()
            except NoResultFound:
                raise RdsNotFoundError("not found")
            except MultipleResultsFound:
                raise RdsError("only one row expected")
            finally:
                cursor.close()
        return result._asdict()

    def get_address_history(
        self, address: str, token: str, limit: int, last_tx: Optional[str], last_ts: int
    ) -> Tuple[bool, List[dict]]:
        """Fetch a page of the transaction history for an address/token pair.

        The page starts after the (`last_ts`, `last_tx`) cursor, or at the newest
        transaction when `last_tx` is None.

        Returns whether there is a next page, and the page's rows.
        """
        params: dict = {"address": address, "token": token, "limit": limit + 1}
        query = address_history_query
        if last_tx is not None:
            query = address_history_after_query
            params.update(last_tx=last_tx, last_ts=last_ts)

        result: List[dict] = []
        with self.engine.connect() as connection:
            cursor = connection.execute(text(query), **params)

            for row in cursor:
                result.append(row._asdict())

        # One row more than the page was fetched to tell whether there is a next page
        return len(result) > limit, result[:limit]

    def get_address_tokens(
        self, address: str, limit: int, offset: int
    ) -> Tuple[int, List[dict]]:
        """Fetch the tokens an address has any history with.

        HTR will always be the first token if HTR is on the token history.
        This is done by querying for HTR first if we are on the first page (`offset` == 0)
        then querying for other tokens.

        The total number of tokens on the address history is also returned.
        """
        result: List[dict] = []
        found_htr: bool = False
        total: int = 0
        with self.engine.connect() as connection:
            # First, we query for total number of tokens on the address history
            cursor = connection.execute(
                text(address_tokens_count_query), address=address
            )
            try:
                count_result = cursor.one()
                total = count_result["total"]
            except (NoResultFound, MultipleResultsFound):
                raise RdsError("Could not fetch token count")
            finally:
                cursor.close()
            if offset == 0:
                # We only search for HTR on the first page
                cursor = connection.execute(
                    text(address_has_htr_query), address=address
                )
                htr = cursor.one_or_none()
                cursor.close()
                if htr:
                    found_htr = True
                    result.append(htr._asdict())

            # Search for custom tokens
            cursor = connection.execute(
                text(address_tokens_query),
                address=address,
                offset=offset,
                limit=(limit - 1) if found_htr else limit,
            )
            for row in cursor:
                result.append(row._asdict())

        return total, result

    def get_address_flags(self, address: str) -> dict:
        """Fetch the address's confidential activity flags.

        `has_confidential_activity`: the address has any shielded output or input.
        `has_hidden_token_activity`: the address has a FullyShielded output or input.
        """
        with self.engine.connect() as connection:
            cursor = connection.execute(text(address_flags_query), address=address)
            try:
                result = cursor.one()
            finally:
                cursor.close()
        return {key: bool(value) for key, value in result._asdict().items()}

    def ping(self, timeout: int = 5) -> Tuple[bool, dict]:
        """Ping the database to check if it's alive."""
        with self.engine.connect() as connection:
            cursor = connection.execute(text(ping_query), timeout=timeout)
            try:
                result = cursor.one()
            finally:
                cursor.close()

        return (len(result) > 0 and result[0] == 1), result._asdict()
