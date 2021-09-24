import logging
from typing import Optional

from requests import ReadTimeout

from domain.node_api.address_balance import AddressBalance
from gateways.clients.cache_client import (
        ADDRESS_BALANCE_BLACKLIST_COLLECTION_NAME,
        ADDRESS_SEARCH_BLACKLIST_COLLECTION_NAME,
        CacheClient
    )
from gateways.clients.hathor_core_client import (
        ADDRESS_BALANCE_ENDPOINT,
        ADDRESS_SEARCH_ENDPOINT,
        HathorCoreClient,
    )

logger = logging.getLogger(__name__)


class NodeApiGateway:
    """ Gateway to interact with the full-node api
    """
    def __init__(
        self,
        hathor_core_client: Optional[HathorCoreClient] = None,
    ) -> None:
        self.hathor_core_client = hathor_core_client or HathorCoreClient()

    # /thin_wallet/address_balance

    def blacklist_address_balance(self, address):
        # No expiration on blacklist
        return self.cache_client.set(
                ADDRESS_BALANCE_BLACKLIST_COLLECTION_NAME,
                address, 1)

    def is_blacklisted_address_balance(self, address):
        return bool(self.cache_client.get(
                ADDRESS_BALANCE_BLACKLIST_COLLECTION_NAME,
                address))

    def get_address_balance(self, address: str) -> AddressBalance:
        """Retrieve address balance from full-node

        :param address: address to get balance for
        :type address: str
        """
        value = self.hathor_core_client.get(
                ADDRESS_BALANCE_ENDPOINT,
                params={'address': address},
                timeout=10,
            )
        return AddressBalance.from_dict(value)

    # /thin_wallet/address_search

    def blacklist_address_search(self, address):
        # No expiration on blacklist
        return self.cache_client.set(
                ADDRESS_SEARCH_BLACKLIST_COLLECTION_NAME,
                address, 1)

    def is_blacklisted_address_search(self, address):
        return bool(self.cache_client.get(
                ADDRESS_SEARCH_BLACKLIST_COLLECTION_NAME,
                address))

    def get_address_search(self, address: str, count: int, page: str, hash: str, token: Optional[str] = None) -> AddressBalance:
        """Retrieve address balance from full-node

        :param address: address to get balance for
        :type address: str
        """
        params = {
            "address": address,
            "count": count,
            "page": page,
            "hash": hash,
        }
        if token:
            params['token'] = token
        value = self.hathor_core_client.get(
                ADDRESS_SEARCH_ENDPOINT,
                params=params,
                timeout=10,
            )
        return AddressBalance.from_dict(value)
