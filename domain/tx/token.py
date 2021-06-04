from dataclasses import asdict, dataclass
from enum import Enum
from typing import Optional


class TokenNFTType(str, Enum):
    VIDEO = 'VIDEO'
    IMAGE = 'IMAGE'


@dataclass
class TokenNFT:
    """Data of token NFT

    :param type: NFT Type. image or video.
    :type type: :py:class:`domain.tx.token.TokenNFTType`

    :param file: Media file of the NFT
    :type file: str
    """
    type: TokenNFTType
    file: str


@dataclass
class TokenMetadata:
    """Metadata of token

    :param id: Token unique id
    :type id: str

    :param verified: If token is verified or not
    :type verified: bool

    :param banned: If token is banned or not
    :type banned: bool

    :param reason: Bannishment reason
    :type reason: str

    :param nft: NFT data, if any.
    :type nft: :py:class:`domain.tx.token.TokenNFT`
    """
    id: str
    verified: bool
    banned: bool
    reason: Optional[str]
    nft: Optional[TokenNFT]

    def to_dict(self) -> dict:
        """ Convert a TokenMetadata instance into dict

        :return: Dict representations of TokenMetadata
        :rtype: dict
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'TokenMetadata':
        """ Creates a new TokenMetadata instance from a given dict (inverse operation of `to_dict`)

        :param dikt: Dict with TokenMetadata structure and data
        :type dikt: dict

        :return: The new instance
        :rtype: :py:class:`domain.tx.token.TokenMetadata`
        """
        if dikt.get('nft'):
            dikt['nft'] = TokenNFT(TokenNFTType(dikt['nft']['type'].upper()), dikt['nft']['file'])

        return TokenMetadata(**dikt)
