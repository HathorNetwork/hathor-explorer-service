from dataclasses import asdict, dataclass
from typing import List, Optional

from dacite import from_dict


@dataclass
class TxInput:
    tx_id: str
    index: int
    data: Optional[str] = None


@dataclass
class TxOutput:
    value: int
    script: str


@dataclass
class Transaction:
    tx_id: str
    timestamp: int
    version: int
    weight: float
    parents: List[str]
    inputs: List[TxInput]
    outputs: List[TxOutput]
    tokens: List[str]

    def to_dict(self) -> dict:
        """ Convert an instance into dict

        :return: The dict representation
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Transaction':
        return from_dict(data_class=cls, data=dikt)
