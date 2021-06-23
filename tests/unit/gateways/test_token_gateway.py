import json
from unittest.mock import MagicMock, patch

from pytest import fixture, raises

from gateways.token_gateway import TokenGateway
from tests.fixtures.hathor_core_fixtures import HATHOR_CORE_GET_TOKEN, HATHOR_CORE_GET_TOKEN_INVALID
from tests.fixtures.token_factory import TokenMetadataFactory, TokenNFTFactory


class TestTokenGateway:

    @fixture
    def s3_client(self):
        return MagicMock()

    @fixture
    def hathor_core_client(self):
        return MagicMock()

    @patch('gateways.token_gateway.TOKEN_METADATA_BUCKET', 'token-metadata')
    def test_get_token_metadata_from_s3(self, s3_client):
        nft = TokenNFTFactory()
        token_metadata = TokenMetadataFactory(nft=nft)

        s3_client.load_file = MagicMock(return_value=json.dumps(token_metadata.to_dict()))

        gateway = TokenGateway(s3_client=s3_client)

        result = gateway.get_token_metadata_from_s3('token-id')

        s3_client.load_file.assert_called_once_with('token-metadata', 'token-id')
        assert result
        assert result.id == token_metadata.id
        assert result.verified == token_metadata.verified
        assert result.banned == token_metadata.banned
        assert result.reason == token_metadata.reason
        assert result.nft.file == token_metadata.nft.file
        assert result.nft.type == token_metadata.nft.type

    @patch('gateways.token_gateway.TOKEN_METADATA_BUCKET', 'token-metadata')
    def test_get_token_metadata_from_s3_return_none(self, s3_client):
        s3_client.load_file = MagicMock(return_value=None)

        gateway = TokenGateway(s3_client=s3_client)

        result = gateway.get_token_metadata_from_s3('token-id')

        s3_client.load_file.assert_called_once_with('token-metadata', 'token-id')

        assert result is None

    @patch('gateways.token_gateway.TOKEN_METADATA_BUCKET', None)
    def test_get_token_metadata_from_s3_raises_exception(self):
        gateway = TokenGateway()

        with raises(Exception, match=r'No bucket name in config'):
            gateway.get_token_metadata_from_s3('token-id')

    def test_get_token(self, hathor_core_client):
        hathor_core_client.get = MagicMock(return_value=HATHOR_CORE_GET_TOKEN)

        gateway = TokenGateway(hathor_core_client=hathor_core_client)

        token_id = '0058dacaa9cb6e120e825fa40f738273f3bf87e82c8b376158695a4fb42e187d'

        token = gateway.get_token(token_id)

        hathor_core_client.get.assert_called_once_with('/v1a/thin_wallet/token', {'id': token_id})

        assert token
        assert token.id == token_id
        assert token.name == 'HTR Token'
        assert token.symbol == 'TOKEN'
        assert token.total_supply == 10000000
        assert token.transactions_count == 11
        assert token.can_melt is True
        assert token.can_mint is True

    def test_get_token_invalid(self, hathor_core_client):
        hathor_core_client.get = MagicMock(return_value=HATHOR_CORE_GET_TOKEN_INVALID)

        gateway = TokenGateway(hathor_core_client=hathor_core_client)

        token = gateway.get_token('something')

        hathor_core_client.get.assert_called_once_with('/v1a/thin_wallet/token', {'id': 'something'})

        assert token is None

    def test_get_token_no_200(self, hathor_core_client):
        hathor_core_client.get = MagicMock(return_value=None)

        gateway = TokenGateway(hathor_core_client=hathor_core_client)

        token = gateway.get_token('something')

        hathor_core_client.get.assert_called_once_with('/v1a/thin_wallet/token', {'id': 'something'})

        assert token is None
