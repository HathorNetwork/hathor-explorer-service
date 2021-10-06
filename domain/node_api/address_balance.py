from dataclasses import asdict, dataclass
from typing import Dict, Optional

from dacite import from_dict


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
    # tokens_data key: token uid, value: address balance for token
    tokens_data: Optional[Dict[str, AddressBalanceTokenData]] = None
    total_transactions: Optional[int] = None
    message: Optional[str] = None

    def to_dict(self) -> dict:
        """ Convert an instance into dict

        :return: The dict representation
        :rtype: dict
        """
        dikt = asdict(self)
        if self.success and 'message' in dikt:
            del dikt['message']
        return dikt

    @classmethod
    def from_dict(cls, dikt: dict) -> 'AddressBalance':
        return from_dict(data_class=cls, data=dikt)
