from typing import List, Optional

from gateways.clients.cache_client import ADDRESS_BLACKLIST_COLLECTION_NAME, CacheClient
from gateways.clients.hathor_core_client import (
    ADDRESS_BALANCE_ENDPOINT,
    ADDRESS_SEARCH_ENDPOINT,
    DASHBOARD_TX_ENDPOINT,
    DECODE_TX_ENDPOINT,
    FEATURE_ENDPOINT,
    GRAPHVIZ_DOT_NEIGHBORS_ENDPOINT,
    NC_BLUEPRINT_INFORMATION_ENDPOINT,
    NC_BLUEPRINT_SOURCE_CODE_ENDPOINT,
    NC_HISTORY_ENDPOINT,
    NC_STATE_ENDPOINT,
    PUSH_TX_ENDPOINT,
    TOKEN_ENDPOINT,
    TOKEN_HISTORY_ENDPOINT,
    TRANSACTION_ENDPOINT,
    TX_ACC_WEIGHT_ENDPOINT,
    VERSION_ENDPOINT,
    HathorCoreClient,
)

# The default lambda timeout for Node API Lambdas is set to
# 6 seconds. Therefore, the client should have a lower timeout,
# to let the lambda shut down gracefully.
NODE_API_TIMEOUT_IN_SECONDS = 5


class NodeApiGateway:
    """Gateway to interact with the full-node api"""

    def __init__(
        self,
        hathor_core_client: Optional[HathorCoreClient] = None,
        cache_client: Optional[CacheClient] = None,
    ) -> None:
        self.hathor_core_client = hathor_core_client or HathorCoreClient()
        self.cache_client = cache_client or CacheClient()

    # /thin_wallet/address_balance

    def blacklist_address(self, address: str) -> Optional[bool]:
        """Blacklist address from calling full-node apis

        :param address: address to blacklist
        :type address: str
        """
        # No expiration on blacklist
        return self.cache_client.set(ADDRESS_BLACKLIST_COLLECTION_NAME, address, 1)

    def is_blacklisted_address(self, address: str) -> bool:
        """Check if address is on the blacklist

        :param address: address to check
        :type address: str
        """
        return bool(self.cache_client.get(ADDRESS_BLACKLIST_COLLECTION_NAME, address))

    def get_address_balance(self, address: str) -> Optional[dict]:
        """Retrieve address balance from full-node

        :param address: address to get balance for
        :type address: str
        """
        return self.hathor_core_client.get(
            ADDRESS_BALANCE_ENDPOINT,
            params={"address": address},
            # lambda timeout 15s, which is the sum of all lambda's steps timeout
            # see: https://github.com/HathorNetwork/hathor-explorer-service/pull/93
            timeout=10,
        )

    def get_address_search(
        self,
        address: str,
        count: int,
        page: Optional[str] = None,
        hash: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[dict]:
        """Retrieve address balance from full-node

        :param address: address to get balance for
        :type address: str
        """
        params = {
            "address": address,
            "count": count,
        }
        if token:
            params["token"] = token
        if hash:
            params["hash"] = hash
        if page:
            params["page"] = page

        return self.hathor_core_client.get(
            ADDRESS_SEARCH_ENDPOINT,
            params=params,
            # lambda timeout 15s, which is the sum of all lambda's steps timeout
            # see: https://github.com/HathorNetwork/hathor-explorer-service/pull/93
            timeout=10,  # lambda timeout 15s
        )

    def get_version(self) -> Optional[dict]:
        """Retrieve version information"""

        return self.hathor_core_client.get(
            VERSION_ENDPOINT, timeout=NODE_API_TIMEOUT_IN_SECONDS
        )

    def get_feature(self, block: Optional[str]) -> Optional[dict]:
        """Retrieve feature information."""
        return self.hathor_core_client.get(
            FEATURE_ENDPOINT,
            params={"block": block},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )

    def get_dashboard_tx(self, block: int, tx: int) -> Optional[dict]:
        """Retrieve info on blocks and transaction to show on dashboard"""

        return self.hathor_core_client.get(
            DASHBOARD_TX_ENDPOINT,
            params={"tx": tx, "block": block},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )

    def get_transaction_acc_weight(self, id: str) -> Optional[dict]:
        """Retrieve acc weight for a tx"""

        return self.hathor_core_client.get(
            TX_ACC_WEIGHT_ENDPOINT,
            params={"id": id},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )

    def get_token_history(
        self,
        id: str,
        count: int,
        hash: Optional[str] = None,
        page: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> Optional[dict]:
        """Retrieve token history"""

        params = {"id": id, "count": count}
        if hash:
            params["hash"] = hash
            params["page"] = page
            params["timestamp"] = timestamp

        return self.hathor_core_client.get(
            TOKEN_HISTORY_ENDPOINT, params=params, timeout=NODE_API_TIMEOUT_IN_SECONDS
        )

    def get_transaction(self, id: str) -> Optional[dict]:
        """Retrieve transaction by id"""
        return self.hathor_core_client.get(
            TRANSACTION_ENDPOINT, params={"id": id}, timeout=NODE_API_TIMEOUT_IN_SECONDS
        )

    def decode_tx(self, hex_tx: str) -> Optional[dict]:
        """Decode a transaction from it's hex encoded struct data."""
        return self.hathor_core_client.get(
            DECODE_TX_ENDPOINT,
            params={"hex_tx": hex_tx},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )

    def push_tx(self, hex_tx: str) -> Optional[dict]:
        """Push a transaction from it's hex encoded struct data."""
        return self.hathor_core_client.post(
            PUSH_TX_ENDPOINT,
            body={"hex_tx": hex_tx},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )

    def graphviz_dot_neighbors(
        self, tx: str, graph_type: str, max_level: int
    ) -> Optional[str]:
        """Generate file with the graph of neighbours of a tx in dot format."""
        data = {
            "tx": tx,
            "graph_type": graph_type,
            "max_level": max_level,
        }
        return self.hathor_core_client.get_text(
            GRAPHVIZ_DOT_NEIGHBORS_ENDPOINT,
            params=data,
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )

    def list_transactions(
        self,
        type: str,
        count: int,
        hash: Optional[str] = None,
        page: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> Optional[dict]:
        """Retrieve list of transactions"""

        params = {"type": type, "count": count}
        if hash:
            params["hash"] = hash
            params["page"] = page
            params["timestamp"] = timestamp

        return self.hathor_core_client.get(
            TRANSACTION_ENDPOINT, params=params, timeout=NODE_API_TIMEOUT_IN_SECONDS
        )

    def get_token(self, id: str) -> Optional[dict]:
        """Retrieve token by id"""
        return self.hathor_core_client.get(
            TOKEN_ENDPOINT, params={"id": id}, timeout=NODE_API_TIMEOUT_IN_SECONDS
        )

    def get_nc_state(
        self, id: str, fields: List[str], balances: List[str], calls: List[str]
    ) -> Optional[dict]:
        """Get state of a nano contract."""
        return self.hathor_core_client.get(
            NC_STATE_ENDPOINT,
            params={
                "id": id,
                "fields[]": fields,
                "balances[]": balances,
                "calls[]": calls,
            },
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )

    def get_nc_history(
        self,
        id: str,
        after: Optional[str] = None,
        before: Optional[str] = None,
        count: Optional[int] = None,
    ) -> Optional[dict]:
        """Get history of a nano contract."""
        return self.hathor_core_client.get(
            NC_HISTORY_ENDPOINT,
            params={"id": id, "after": after, "count": count, "before": before},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )

    def get_nc_blueprint_information(self, blueprint_id: str) -> Optional[dict]:
        """Get blueprint information."""
        return self.hathor_core_client.get(
            NC_BLUEPRINT_INFORMATION_ENDPOINT,
            params={"blueprint_id": blueprint_id},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )

    def get_nc_blueprint_source_code(self, blueprint_id: str) -> Optional[dict]:
        """Get blueprint source code."""
        return self.hathor_core_client.get(
            NC_BLUEPRINT_SOURCE_CODE_ENDPOINT,
            params={"blueprint_id": blueprint_id},
            timeout=NODE_API_TIMEOUT_IN_SECONDS,
        )
