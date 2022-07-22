from dataclasses import asdict, dataclass

from dacite import from_dict


@dataclass
class TokenBalance:
    """ Address Balance for a token.

    :param token_id: Token unique id
    :type token_id: str

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
    def from_dict(cls, dikt: dict) -> 'TokenBalance':
        return from_dict(data_class=cls, data=dikt)


@dataclass
class TxHistoryEntry:
    """ Transaction history item.

    :param tx_id: Transaction unique id
    :type tx_id: str

    :param token_id: Token unique id
    :type token_id: str

    :param timestamp: Transaction timestamp
    :type timestamp: int

    :param balance: Transaction balance for the token
    :type balance: int

    :param version: Transaction version
    :type type: int

    :param height: Transaction height
    :type height: int
    """

    tx_id: str
    token_id: str
    timestamp: int
    balance: int
    version: int
    height: int

    def to_dict(self) -> dict:
        """ Convert an instance into dict

        :return: Dict representation
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'TxHistoryEntry':
        return from_dict(data_class=cls, data=dikt)


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

    def to_dict(self) -> dict:
        """ Convert an instance into dict

        :return: Dict representation
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'TokenEntry':
        token_id = dikt.get('token_id')
        if token_id == '00':
            return cls(token_id='00', name='Hathor', symbol='HTR')
        return from_dict(data_class=cls, data=dikt)
