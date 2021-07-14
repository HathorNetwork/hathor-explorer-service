from dataclasses import dataclass, asdict
from enum import Enum


class MetadataType(str, Enum):
    TOKEN = 'TOKEN'
    TRANSACTION = 'TRANSACTION'


@dataclass(init=False)
class Metadata:
    id: str

    @property
    def type(self) -> MetadataType:
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

    @data.setter
    def data(self, value):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, dikt: dict):
        raise NotImplementedError

    def to_dict(self) -> dict:
        """ Convert a Metadata instance into dict

        :return: Dict representations of Metadata
        :rtype: dict
        """
        return asdict(self)
