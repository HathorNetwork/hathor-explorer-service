from dataclasses import dataclass
from enum import Enum
from typing import Optional

from domain.metadata.metadata import Metadata, MetadataType


class TokenNFTMediaType(str, Enum):
    VIDEO = 'VIDEO'
    IMAGE = 'IMAGE'
    AUDIO = 'AUDIO'


@dataclass
class TokenNFTMedia:
    """Data of token NFT

    :param type: NFT Type. image or video.
    :type type: :py:class:`domain.metadata.token_metdata.TokenNFTMediaType`

    :param file: Media file of the NFT
    :type file: str

    :param loop: If media will play in loop or not. Works for audio and video as well
    :type loop: Optional[bool]

    :param autoplay: If media will play automatically or not. Works for audio and video as well
    :type autoplay: Optional[bool]
    """
    type: TokenNFTMediaType
    file: str
    loop: Optional[bool] = False
    autoplay: Optional[bool] = False


@dataclass
class MetaToken:
    """Metadata of a token

    :param id: Token unique id
    :type id: str

    :param verified: If token is verified or not. None and False are equivalent
    :type verified: Optional[bool]

    :param banned: If token is banned or not. None and False are equivalent
    :type banned: Optional[bool]

    :param reason: Bannishment reason
    :type reason: Optional[str]

    :param nft: If token is a nft or not. None and False are equivalent
    :type nft: Optional[bool]

    :param nft_media: NFT media data, if any.
    :type nft_media: Optional[:py:class:`domain.metadata.token_metdata.TokenNFTMedia`]
    """
    id: str
    verified: Optional[bool] = False
    banned: Optional[bool] = False
    reason: Optional[str] = ''
    nft: Optional[bool] = False
    nft_media: Optional[TokenNFTMedia] = None


@dataclass
class TokenMetadata(Metadata):
    data: Optional[MetaToken] = None
    type: MetadataType = MetadataType.TOKEN

    @classmethod
    def from_dict(cls, dikt: dict) -> 'TokenMetadata':
        """ Creates a new TokenMetadata instance from a given dict (inverse operation of `to_dict`)

        :param dikt: Dict with TokenMetadata structure and data
        :type dikt: dict

        :return: The new instance
        :rtype: :py:class:`domain.metadata.token_metdata.TokenMetadata`
        """
        data = dikt.get('data', {})
        if data.get('nft_media'):
            data['nft_media'] = TokenNFTMedia(
                TokenNFTMediaType(data['nft_media']['type'].upper()),
                data['nft_media']['file'],
                data['nft_media'].get('loop', None)
            )

        return cls(
            id=dikt['id'],
            data=MetaToken(**data)
        )
