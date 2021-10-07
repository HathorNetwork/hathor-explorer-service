from typing import Optional

from gateways.clients.cache_client import ADDRESS_BLACKLIST_COLLECTION_NAME, CacheClient
from gateways.clients.hathor_core_client import ADDRESS_BALANCE_ENDPOINT, ADDRESS_SEARCH_ENDPOINT, HathorCoreClient


class NodeApiGateway:
    """ Gateway to interact with the full-node api
    """
    def __init__(
        self,
        hathor_core_client: Optional[HathorCoreClient] = None,
        cache_client: Optional[CacheClient] = None,
    ) -> None:
        self.hathor_core_client = hathor_core_client or HathorCoreClient()
        self.cache_client = cache_client or CacheClient()

    # /thin_wallet/address_balance

    def blacklist_address(self, address: str) -> Optional[bool]:
        """ Blacklist address from calling full-node apis

        :param address: address to blacklist
        :type address: str
        """
        # No expiration on blacklist
        return self.cache_client.set(
                ADDRESS_BLACKLIST_COLLECTION_NAME,
                address, 1)

    def is_blacklisted_address(self, address: str) -> bool:
        """ Check if address is on the blacklist

        :param address: address to check
        :type address: str
        """
        return bool(self.cache_client.get(
                ADDRESS_BLACKLIST_COLLECTION_NAME,
                address))

    def get_address_balance(self, address: str) -> Optional[dict]:
        """Retrieve address balance from full-node

        :param address: address to get balance for
        :type address: str
        """
        return self.hathor_core_client.get(
                ADDRESS_BALANCE_ENDPOINT,
                params={'address': address},
                timeout=10,
            )

    def get_address_search(
            self, address: str, count: int, page: Optional[str] = None,
            hash: Optional[str] = None, token: Optional[str] = None) -> Optional[dict]:
        """Retrieve address balance from full-node

        :param address: address to get balance for
        :type address: str
        """
        params = {
            "address": address,
            "count": count,
        }
        if token:
            params['token'] = token
        if hash:
            params['hash'] = hash
        if page:
            params['page'] = page

        return self.hathor_core_client.get(
                ADDRESS_SEARCH_ENDPOINT,
                params=params,
                timeout=10,
            )
