from dataclasses import asdict, dataclass

from dacite import from_dict


@dataclass
class Token:
    """Hathor Token

    :param id: Token unique id
    :type id: str

    :param name: Token name
    :type name: str

    :param symbol: Token symbol
    :type symbol: str

    :param total_supply: Token total supply
    :type total_supply: int

    :param transactions_count: Number of transactions of the Token
    :type transactions_count: int

    :param can_mint: True if can mint new Tokens, False othwerwise
    :type can_mint: bool

    :param can_melt: True if can melt Tokens, False otherwise
    :type can_melt: bool
    """
    id: str
    name: str
    symbol: str
    total_supply: int
    transactions_count: int
    can_mint: bool
    can_melt: bool

    def to_dict(self) -> dict:
        """ Convert a Token instance into dict

        :return: Dict representations of Token
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Token':
        """ Creates a new Token instance from a given dict (inverse operation of `to_dict`)

        :param dikt: Dict with Token structure and data
        :type dikt: dict

        :return: The new instance
        :rtype: :py:class:`domain.tx.token.Token`
        """
        return from_dict(data_class=cls, data=dikt)
