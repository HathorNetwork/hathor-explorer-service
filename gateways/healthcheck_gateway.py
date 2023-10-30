from typing import Optional, Tuple
from gateways.clients.cache_client import CacheClient
from gateways.clients.elastic_search_client import ElasticSearchClient
from common.configuration import ELASTIC_INDEX

from gateways.clients.hathor_core_client import (
    VERSION_ENDPOINT,
    HathorCoreAsyncClient,
)
from gateways.clients.wallet_service_db_client import WalletServiceDBClient

# The default lambda timeout for the Healtcheck Lambda is set to
# 6 seconds. Therefore, the client should have a lower timeout,
# to let the lambda shut down gracefully.
HEALTHCHECK_CLIENT_TIMEOUT_IN_SECONDS = 5

class HealthcheckGateway:
    def __init__(
        self,
        hathor_core_async_client: Optional[HathorCoreAsyncClient] = None,
        cache_client: Optional[CacheClient] = None,
        elastic_search_client: Optional[ElasticSearchClient] = None,
        wallet_service_db_client: Optional[WalletServiceDBClient] = None,
    ) -> None:
        self.hathor_core_async_client = hathor_core_async_client or HathorCoreAsyncClient()
        self.cache_client = cache_client or CacheClient()
        # The index we provide here doesn't make much difference for the healthcheck
        self.elastic_search_client = elastic_search_client or ElasticSearchClient(ELASTIC_INDEX)
        self.wallet_service_db_client = wallet_service_db_client or WalletServiceDBClient()


    async def get_hathor_core_version(self) -> Optional[dict]:
        """Retrieve hathor-core version information"""

        return await self.hathor_core_async_client.get(
            VERSION_ENDPOINT, timeout=HEALTHCHECK_CLIENT_TIMEOUT_IN_SECONDS
        )

    def ping_redis(self) -> bool:
        """Ping redis to check if it's alive"""

        return self.cache_client.ping()

    def get_elasticsearch_health(self) -> dict:
        """Retrieve elasticsearch health information"""

        return self.elastic_search_client.health()

    def ping_wallet_service_db(self) -> Tuple[bool, str]:
        """Ping the database to check if it's alive"""

        return self.wallet_service_db_client.ping()