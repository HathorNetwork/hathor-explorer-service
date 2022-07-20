from typing import TYPE_CHECKING, Optional, List
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from common.errors import RdsError, RdsNotFoundError
from common.configuration import WALLET_SERVICE_USERNAME, WALLET_SERVICE_PASSWORD, WALLET_SERVICE_HOST, WALLET_SERVICE_DB

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine, Row


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
WHERE voided = FALSE AND address = ? AND token_id = ?'''

address_history_query: str = '''\
SELECT tx_id, token_id, balance, timestamp
FROM address_tx_history
ORDER BY timestamp DESC
WHERE voided = FALSE AND address = ? AND token_id = ?
OFFSET ? ROWS FETCH FIRST ? ROWS ONLY'''

address_tokens_query: str = '''\
SELECT token.id AS token_id, token.name AS name, token.symbol AS symbol
FROM token INNER JOIN address_balance ON token.id = address_balance.token_id
WHERE address_balance.address = ?'''


class WalletServiceDBClient:

    def __init__(self, engine: Optional['Engine'] = None):
        self.engine = engine or get_engine()

    def get_address_balance(self, address: str, token: str) -> 'Row':
        result: 'Row'
        with self.engine.connect() as connection:
            cursor = connection.execute(text(address_balance_query))
            try:
                result = cursor.one()
            except NoResultFound:
                raise RdsNotFoundError('not found')
            except (NoResultFound, MultipleResultsFound):
                raise RdsError('only one row expected')
            finally:
                cursor.close()
        return result

    def get_address_history(self, address: str, token: str, count: int, skip: int) -> List['Row']:
        result: List['Row'] = []
        with self.engine.connect() as connection:
            cursor = connection.execute(text(address_history_query))
            result = cursor.all()

        return result

    def get_address_tokens(self, address: str) -> List['Row']:
        result = List['Row'] = []
        with self.engine.connect() as connection:
            cursor = connection.execute(text(address_tokens_query))
            result = cursor.all()
        return result
