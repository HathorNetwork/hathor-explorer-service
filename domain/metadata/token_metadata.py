from typing import Optional
from dataclasses import dataclass
from enum import Enum

from domain.metadata.metadata import Metadata, MetadataType


class TokenNFTType(str, Enum):
    VIDEO = 'VIDEO'
    IMAGE = 'IMAGE'
    AUDIO = 'AUDIO'


@dataclass
class TokenNFT:
    """Data of token NFT

    :param type: NFT Type. image or video.
    :type type: :py:class:`domain.metadata.token_metdata.TokenNFTType`

    :param file: Media file of the NFT
    :type file: str
    """
    type: TokenNFTType
    file: str


@dataclass
class MetaToken:
    """Metadata of a token

    :param id: Token unique id
    :type id: str

    :param verified: If token is verified or not
    :type verified: bool

    :param banned: If token is banned or not
    :type banned: bool

    :param reason: Bannishment reason
    :type reason: str

    :param nft: NFT data, if any.
    :type nft: :py:class:`domain.metadata.token_metdata.TokenNFT`
    """
    id: str
    verified: Optional[bool] = False
    banned: Optional[bool] = False
    reason: Optional[str] = ''
    nft: Optional[TokenNFT] = None


@dataclass
class TokenMetadata(Metadata):
    _data: MetaToken
    type: MetadataType = MetadataType.TOKEN

    @property
    def data(self) -> MetaToken:
        return self._data

    @data.setter
    def data(self, value: MetaToken):
        self._data = value

    @classmethod
    def from_dict(cls, dikt: dict) -> 'TokenMetadata':
        """ Creates a new TokenMetadata instance from a given dict (inverse operation of `to_dict`)

        :param dikt: Dict with TokenMetadata structure and data
        :type dikt: dict

        :return: The new instance
        :rtype: :py:class:`domain.metadata.token_metdata.TokenMetadata`
        """
        if dikt.get('nft'):
            dikt['nft'] = TokenNFT(TokenNFTType(dikt['nft']['type'].upper()), dikt['nft']['file'])

        return cls(
            id=dikt['id'],
            data=MetaToken(**dikt)
        )
