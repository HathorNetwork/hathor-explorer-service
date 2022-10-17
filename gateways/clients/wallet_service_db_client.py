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


address_balance_query: str = """\
SELECT
    token_id,
    transactions,
    total_received,
    unlocked_balance,
    locked_balance,
    unlocked_authorities,
    locked_authorities
FROM address_balance
WHERE address = :address AND token_id = :token LIMIT 1"""

address_history_query = """\
  SELECT address_tx_history.tx_id AS tx_id,
         address_tx_history.token_id AS token_id,
         address_tx_history.balance AS balance,
         address_tx_history.timestamp AS timestamp,
         transaction.version AS version,
         transaction.height AS height,
         (
          SELECT 1 FROM address_tx_history
           WHERE address_tx_history.address = :address
             AND (
                ((ISNULL(:last_tx) = 0) AND (address_tx_history.timestamp, address_tx_history.tx_id) < (:last_ts, :last_tx))
                OR
                ((ISNULL(:last_tx) = 1) AND (address_tx_history.timestamp, address_tx_history.tx_id) > (0, NULL))
             )
             AND address_tx_history.token_id = :token
           LIMIT 1
          OFFSET :limit
         ) AS has_next
    FROM address_tx_history INNER JOIN transaction ON address_tx_history.tx_id = transaction.tx_id
   WHERE transaction.voided = FALSE
     AND address_tx_history.address = :address
     AND address_tx_history.token_id = :token
     AND (
        ((ISNULL(:last_tx) = 0) AND (address_tx_history.timestamp, address_tx_history.tx_id) < (:last_ts, :last_tx))
        OR
        ((ISNULL(:last_tx) = 1) AND (address_tx_history.timestamp, address_tx_history.tx_id) > (0, NULL))
     )
ORDER BY timestamp DESC, tx_id DESC
   LIMIT :limit"""

address_tokens_query: str = """\
    SELECT token.id AS token_id,
           token.name AS name,
           token.symbol AS symbol
      FROM token
INNER JOIN (
             SELECT token_id,
                    MAX(timestamp) AS timestamp
               FROM address_tx_history
              WHERE address = :address
                AND token_id != '00'
           GROUP BY token_id
           ) address_tokens
        ON token.id = address_tokens.token_id
  ORDER BY address_tokens.timestamp DESC
LIMIT :limit OFFSET :offset"""

address_has_htr_query: str = """\
SELECT '00' as token_id, 'Hathor' as name, 'HTR' as symbol
WHERE EXISTS (SELECT 1 FROM address_balance WHERE address = :address and token_id = '00')
"""

address_tokens_count_query = """\
SELECT COUNT(*) as total
FROM token INNER JOIN address_balance
ON token.id = address_balance.token_id
WHERE address_balance.address = :address"""


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
        self, address: str, token: str, limit: int, last_tx: str, last_ts: int
    ) -> List[dict]:
        """Fetch the transaction history for an address/token pair."""
        result: List[dict] = []
        with self.engine.connect() as connection:
            cursor = connection.execute(
                text(address_history_query),
                address=address,
                token=token,
                limit=limit,
                last_tx=last_tx,
                last_ts=last_ts,
            )

            for row in cursor:
                result.append(row._asdict())

        return result

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
