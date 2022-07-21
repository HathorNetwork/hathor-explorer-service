from typing import TYPE_CHECKING, Optional, List
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from common.errors import RdsError, RdsNotFoundError
from common.configuration import WALLET_SERVICE_USERNAME, WALLET_SERVICE_PASSWORD, WALLET_SERVICE_HOST, WALLET_SERVICE_DB

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


wallet_service_url = sqlalchemy.engine.url.URL(
        'mysql+pymysql',
        username=WALLET_SERVICE_USERNAME,
        password=WALLET_SERVICE_PASSWORD,
        host=WALLET_SERVICE_HOST,
        port=3306,
        database=WALLET_SERVICE_DB)
wallet_service_engine = sqlalchemy.create_engine(wallet_service_url, echo=True)


def get_engine():
    """ Returns the engine for connecting with the wallet service database."""
    return wallet_service_engine


address_balance_query: str = '''\
SELECT token_id, transactions, unlocked_balance, locked_balance, unlocked_authorities, locked_authorities
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
LIMIT :count OFFSET :skip'''


address_tokens_query: str = '''\
SELECT address_balance.token_id AS token_id, token.name AS name, token.symbol AS symbol
FROM token RIGHT OUTER JOIN address_balance ON token.id = address_balance.token_id
WHERE address_balance.address = :address'''


class WalletServiceDBClient:

    def __init__(self, engine: Optional['Engine'] = None):
        self.engine = engine or get_engine()

    def get_address_balance(self, address: str, token: str) -> dict:
        result: dict
        with self.engine.connect() as connection:
            cursor = connection.execute(text(address_balance_query), address=address, token=token)
            try:
                result = cursor.one()
            except NoResultFound:
                raise RdsNotFoundError('not found')
            except (NoResultFound, MultipleResultsFound):
                raise RdsError('only one row expected')
            finally:
                cursor.close()
        return result._asdict()

    def get_address_history(self, address: str, token: str, count: int, skip: int) -> List[dict]:
        result: List[dict] = []
        with self.engine.connect() as connection:
            cursor = connection.execute(text(address_history_query), address=address, token=token, skip=skip, count=count)
            for row in cursor:
                result.append(row._asdict())

        return result

    def get_address_tokens(self, address: str) -> List[dict]:
        result: List[dict] = []
        with self.engine.connect() as connection:
            cursor = connection.execute(text(address_tokens_query), address=address)
            for row in cursor:
                result.append(row._asdict())
        return result
