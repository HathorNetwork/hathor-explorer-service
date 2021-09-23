from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from dacite import from_dict

from domain.tx.token import Token


@dataclass
class AddressBalanceTokenData:
    name: str
    symbol: str
    received: int
    spent: int


@dataclass
class AddressBalance:

    success: bool
    # The next fields are optional to parse when success is False
    tokens_data: Optional[Dict[str, AddressBalanceTokenData]] = None
    total_transactions: Optional[int] = None
    message: Optional[str] = None

    def to_dict(self) -> dict:
        """ Convert an instance into dict

        :return: The dict representation
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'AddressBalance':
        return from_dict(data_class=cls, data=dikt)
