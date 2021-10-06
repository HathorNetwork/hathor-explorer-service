from dataclasses import asdict, dataclass
from typing import List, Optional

from dacite import from_dict

from domain.node_api.transaction import Transaction


@dataclass
class AddressSearch:

    success: bool
    # TODO: make a more detailed transaction
    transactions: Optional[List[Transaction]] = None
    has_more: Optional[bool] = None
    total: Optional[int] = None
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
    def from_dict(cls, dikt: dict) -> 'AddressSearch':
        return from_dict(data_class=cls, data=dikt)
