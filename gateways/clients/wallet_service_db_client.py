from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.engine import URL, create_engine
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

from common.configuration import (
    ENVIRONMENT,
    WALLET_SERVICE_DB,
    WALLET_SERVICE_HOST,
    WALLET_SERVICE_PASSWORD,
    WALLET_SERVICE_USERNAME,
)
from common.errors import RdsError, RdsNotFoundError

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine, Row


address_balance_query: str = '''\
SELECT
    token_id,
    transactions,
    total_received,
    unlocked_balance,
    locked_balance,
    unlocked_authorities,
    locked_authorities
FROM address_balance
WHERE address = :address AND token_id = :token LIMIT 1'''

address_history_query: str = '''\
SELECT  address_tx_history.tx_id AS tx_id,
        address_tx_history.token_id AS token_id,
        address_tx_history.balance AS balance,
        address_tx_history.timestamp AS timestamp,
        transaction.version AS version,
        transaction.height AS height
FROM address_tx_history INNER JOIN transaction ON address_tx_history.tx_id = transaction.tx_id
WHERE transaction.voided = FALSE AND address_tx_history.address = :address AND address_tx_history.token_id = :token
ORDER BY timestamp DESC
LIMIT :limit OFFSET :offset'''


address_tokens_query: str = '''\
SELECT address_balance.token_id AS token_id,
       token.name AS name,
       token.symbol AS symbol,
       COUNT(*) OVER() as total,
FROM token RIGHT OUTER JOIN address_balance ON token.id = address_balance.token_id
WHERE address_balance.address = :address
ORDER BY address_balance.updated_at DESC
LIMIT :limit OFFSET :offset'''


def get_engine():
    """ Returns the engine for connecting with the wallet service database.

        NullPool is used to disable connection pooling
        making each connect/disconnect actually grab a connection and release the connection.
    """
    wallet_service_url = URL(
            'mysql+pymysql',
            username=WALLET_SERVICE_USERNAME,
            password=WALLET_SERVICE_PASSWORD,
            host=WALLET_SERVICE_HOST,
            port=3306,
            database=WALLET_SERVICE_DB)

    return create_engine(wallet_service_url, poolclass=NullPool, echo=ENVIRONMENT.is_dev)


class WalletServiceDBClient:

    def __init__(self, engine: Optional['Engine'] = None):
        self.engine = engine or get_engine()

    def get_address_balance(self, address: str, token: str) -> dict:
        result: 'Row'
        with self.engine.connect() as connection:
            cursor = connection.execute(text(address_balance_query), address=address, token=token)
            try:
                result = cursor.one()
            except NoResultFound:
                raise RdsNotFoundError('not found')
            except MultipleResultsFound:
                raise RdsError('only one row expected')
            finally:
                cursor.close()
        return result._asdict()

    def get_address_history(self, address: str, token: str, limit: int, offset: int) -> List[dict]:
        result: List[dict] = []
        with self.engine.connect() as connection:
            cursor = connection.execute(
                    text(address_history_query), address=address, token=token, offset=offset, limit=limit)
            for row in cursor:
                result.append(row._asdict())

        return result

    def get_address_tokens(self, address: str, limit: int, offset: int) -> List[dict]:
        result: List[dict] = []
        with self.engine.connect() as connection:
            cursor = connection.execute(text(address_tokens_query), address=address, offset=offset, limit=limit)
            for row in cursor:
                result.append(row._asdict())
        return result
