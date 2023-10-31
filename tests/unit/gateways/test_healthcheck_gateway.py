import unittest
from unittest.mock import MagicMock, patch

from gateways.healthcheck_gateway import HealthcheckGateway


class TestHealthcheckGateway(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hathor_core_async_client = MagicMock()
        self.cache_client = MagicMock()
        self.elastic_search_client = MagicMock()
        self.wallet_service_db_client = MagicMock()

        self.healthcheck_gateway = HealthcheckGateway(
            hathor_core_async_client=self.hathor_core_async_client,
            cache_client=self.cache_client,
            elastic_search_client=self.elastic_search_client,
            wallet_service_db_client=self.wallet_service_db_client,
        )

    async def test_get_hathor_core_version(self):
        async def mock_get_hathor_core_version(endpoint, **kwargs):
            return {"version": "0.39.0"}

        self.hathor_core_async_client.get.side_effect = mock_get_hathor_core_version
        result = await self.healthcheck_gateway.get_hathor_core_version()
        self.assertEqual(result, {"version": "0.39.0"})
        self.hathor_core_async_client.get.assert_called_once_with(
            "/v1a/version", timeout=5
        )

    def test_ping_redis(self):
        self.cache_client.ping.return_value = True
        result = self.healthcheck_gateway.ping_redis()
        self.assertTrue(result)
        self.cache_client.ping.assert_called_once()

    def test_get_elasticsearch_health(self):
        self.elastic_search_client.health.return_value = {"status": "green"}
        result = self.healthcheck_gateway.get_elasticsearch_health()
        self.assertEqual(result, {"status": "green"})
        self.elastic_search_client.health.assert_called_once()

    def test_ping_wallet_service_db(self):
        self.wallet_service_db_client.ping.return_value = (True, "pong")
        result = self.healthcheck_gateway.ping_wallet_service_db()
        self.assertEqual(result, (True, "pong"))
        self.wallet_service_db_client.ping.assert_called_once()
