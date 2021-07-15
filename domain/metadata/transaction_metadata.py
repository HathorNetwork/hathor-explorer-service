from dataclasses import dataclass
from typing import Optional

from domain.metadata.metadata import Metadata, MetadataType


@dataclass
class MetaTransaction:
    id: str
    context: Optional[str]
    genesis: Optional[bool]


@dataclass
class TransactionMetadata(Metadata):
    data: Optional[MetaTransaction] = None
    type: MetadataType = MetadataType.TRANSACTION

    @classmethod
    def from_dict(cls, dikt: dict) -> 'TransactionMetadata':
        """ Creates a new TransactionMetadata instance from a given dict (inverse operation of `to_dict`)

        :param dikt: Dict with TransactionMetadata structure and data
        :type dikt: dict

        :return: The new instance
        :rtype: :py:class:`domain.metadata.token_metdata.TransactionMetadata`
        """

        return cls(
            id=dikt['id'],
            data=MetaTransaction(**dikt['data'])
        )
