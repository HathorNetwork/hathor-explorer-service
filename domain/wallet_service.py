from typing import TYPE_CHECKING, Optional
from dataclasses import asdict, dataclass

if TYPE_CHECKING:
    from sqlalchemy.engine import Row


@dataclass
class TokenBalance:
    """ Address Balance for a token.

    :param token_id: Token unique id
    :type token_id: str

    :param name: Token name
    :type name: str

    :param symbol: Token symbol
    :type symbol: str

    :param unlocked_balance: Address unlocked balance of the token
    :type unlocked_balance: int

    :param locked_balance: Address locked balance of the token
    :type locked_balance: int

    :param unlocked_authorities: Address unlocked authorities of the token
    :type unlocked_authorities: int

    :param locked_authorities: Address locked authorities of the token
    :type locked_authorities: int
    """

    token_id: str
    name: str
    symbol: str
    unlocked_balance: int
    locked_balance: int
    unlocked_authorities: int
    locked_authorities: int
    transactions: int

    def to_dict(self) -> dict:
        """ Convert an instance into dict

        :return: Dict representation
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_row(cls, row: 'Row') -> 'TokenBalance':
        return cls(
            token_id=row[0],
            name=row[1],
            symbol=row[2],
            unlocked_balance=row[3],
            locked_balance=row[4],
            unlocked_authorities=row[5],
            locked_authorities=row[6],
        )


@dataclass
class TxHistoryEntry:
    """ Transaction history item.

    :param tx_id: Transaction unique id
    :type tx_id: str

    :param token_uid: Token unique id
    :type token_uid: str

    :param timestamp: Transaction timestamp
    :type timestamp: int

    :param balance: Transaction balance for the token
    :type balance: int

    :param type: Type of transaction ['tx', 'block']
    :type type: str
    """

    tx_id: str
    token_uid: str
    timestamp: int
    balance: int
    type: str

    def to_dict(self) -> dict:
        """ Convert an instance into dict

        :return: Dict representation
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_row(cls, row: 'Row') -> 'TxHistoryEntry':
        return cls(
            tx=row[0],
            token_id=row[1],
            timestamp=row[2],
            balance=row[3],
            type=row[4],
        )


@dataclass
class TokenEntry:
    """ Token table entry.

    :param token_id: Token unique id
    :type token_id: str

    :param name: Token name
    :type name: str

    :param symbol: Token symbol
    :type symbol: str

    :param createdAt: Timestamp this entry was created
    :type createdAt: int

    :param updatedAt: Last update timestamp
    :type updatedAt: int
    """

    token_id: str
    name: str
    symbol: str
    createdAt: Optional[int] = None
    updateddAt: Optional[int] = None

    def to_dict(self) -> dict:
        """ Convert an instance into dict

        :return: Dict representation
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_row(cls, row: 'Row') -> 'TokenEntry':
        return cls(
            token_id=row[0],
            name=row[1],
            symbol=row[2],
        )
