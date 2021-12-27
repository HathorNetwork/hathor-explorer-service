from typing import Optional

from gateways.clients.cache_client import ADDRESS_BLACKLIST_COLLECTION_NAME, CacheClient
from gateways.clients.hathor_core_client import (
    ADDRESS_BALANCE_ENDPOINT,
    ADDRESS_SEARCH_ENDPOINT,
    DASHBOARD_TX_ENDPOINT,
    DECODE_TX_ENDPOINT,
    GRAPHVIZ_DOT_NEIGHBORS_ENDPOINT,
    PUSH_TX_ENDPOINT,
    TOKEN_ENDPOINT,
    TOKEN_HISTORY_ENDPOINT,
    TRANSACTION_ENDPOINT,
    TX_ACC_WEIGHT_ENDPOINT,
    VERSION_ENDPOINT,
    HathorCoreClient,
)


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

    def get_version(self) -> Optional[dict]:
        """Retrieve version information
        """

        return self.hathor_core_client.get(VERSION_ENDPOINT)

    def get_dashboard_tx(self, block: int, tx: int) -> Optional[dict]:
        """Retrieve info on blocks and transaction to show on dashboard
        """

        return self.hathor_core_client.get(DASHBOARD_TX_ENDPOINT, params={'tx': tx, 'block': block})

    def get_transaction_acc_weight(self, id: str) -> Optional[dict]:
        """Retrieve acc weight for a tx
        """

        return self.hathor_core_client.get(TX_ACC_WEIGHT_ENDPOINT, params={'id': id})

    def get_token_history(
            self,
            id: str,
            count: int,
            hash: Optional[str] = None,
            page: Optional[str] = None,
            timestamp: Optional[int] = None) -> Optional[dict]:
        """Retrieve token history
        """

        params = {'id': id, 'count': count}
        if hash:
            params['hash'] = hash
            params['page'] = page
            params['timestamp'] = timestamp

        return self.hathor_core_client.get(TOKEN_HISTORY_ENDPOINT, params=params)

    def get_transaction(self, id: str) -> Optional[dict]:
        """Retrieve transaction by id
        """
        return self.hathor_core_client.get(TRANSACTION_ENDPOINT, params={'id': id})

    def decode_tx(self, hex_tx: str) -> Optional[dict]:
        """Decode a transaction from it's hex encoded struct data."""
        return self.hathor_core_client.get(DECODE_TX_ENDPOINT, params={'hex_tx': hex_tx})

    def push_tx(self, hex_tx: str) -> Optional[dict]:
        """Push a transaction from it's hex encoded struct data."""
        return self.hathor_core_client.get(PUSH_TX_ENDPOINT, params={'hex_tx': hex_tx})

    def graphviz_dot_neighbors(self, tx: str, graph_type: str, max_level: int) -> Optional[dict]:
        """Generate file with the graph of neighbours of a tx in dot format."""
        data = {
            "tx": tx,
            "graph_type": graph_type,
            "max_level": max_level,
        }
        return self.hathor_core_client.get(GRAPHVIZ_DOT_NEIGHBORS_ENDPOINT, params=data)

    def list_transactions(
            self,
            type: str,
            count: int,
            hash: Optional[str] = None,
            page: Optional[str] = None,
            timestamp: Optional[int] = None) -> Optional[dict]:
        """Retrieve list of transactions
        """

        params = {'type': type, 'count': count}
        if hash:
            params['hash'] = hash
            params['page'] = page
            params['timestamp'] = timestamp

        return self.hathor_core_client.get(TRANSACTION_ENDPOINT, params=params)

    def get_token(self, id: str) -> Optional[dict]:
        """Retrieve token by id
        """
        return self.hathor_core_client.get(TOKEN_ENDPOINT, params={'id': id})

    def list_tokens(self) -> Optional[dict]:
        """Retrieve list of tokens
        """
        return self.hathor_core_client.get(TOKEN_ENDPOINT)
