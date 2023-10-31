import unittest
from unittest.mock import ANY, MagicMock, patch

from usecases.healthcheck import GetHealthcheck


class TestGetHealthcheck(unittest.TestCase):
    def setUp(self):
        self.mock_healthcheck_gateway = MagicMock()

        with patch(
            "usecases.healthcheck.HEALTHCHECK_WALLET_SERVICE_DB_ENABLED", True
        ), patch(
            "usecases.healthcheck.HEALTHCHECK_REDIS_ENABLED", True
        ), patch(
            "usecases.healthcheck.HEALTHCHECK_ELASTICSEARCH_ENABLED", True
        ):
            self.get_healthcheck = GetHealthcheck(
                healthcheck_gateway=self.mock_healthcheck_gateway
            )

    def test_all_components_healthy(self):
        async def mock_get_hathor_core_version():
            return {"version": "0.38.0"}

        self.mock_healthcheck_gateway.get_hathor_core_version.side_effect = (
            mock_get_hathor_core_version
        )
        self.mock_healthcheck_gateway.ping_wallet_service_db.return_value = (True, "1")
        self.mock_healthcheck_gateway.ping_redis.return_value = True
        self.mock_healthcheck_gateway.get_elasticsearch_health.return_value = {
            "status": "green"
        }

        response, status_code = self.get_healthcheck.get_service_health()

        self.assertEqual(status_code, 200)
        self.assertEqual(
            response,
            {
                "status": "pass",
                "description": "Health status of Explorer Service",
                "checks": {
                    "fullnode": [
                        {
                            "status": "pass",
                            "output": "Fullnode is healthy",
                            "componentName": "fullnode",
                            "componentType": "http",
                            "time": ANY,
                        }
                    ],
                    "wallet_service_db": [
                        {
                            "status": "pass",
                            "output": "Wallet service DB is healthy",
                            "componentName": "wallet_service_db",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "redis": [
                        {
                            "status": "pass",
                            "output": "Redis is healthy",
                            "componentName": "redis",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "elasticsearch": [
                        {
                            "status": "pass",
                            "output": "{'status': 'green'}",
                            "componentName": "elasticsearch",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                },
            },
        )

    def test_hathor_core_returns_error(self):
        async def mock_get_hathor_core_version():
            return {"error": "Unable to connect"}

        self.mock_healthcheck_gateway.get_hathor_core_version.side_effect = (
            mock_get_hathor_core_version
        )
        self.mock_healthcheck_gateway.ping_wallet_service_db.return_value = (True, "1")
        self.mock_healthcheck_gateway.ping_redis.return_value = True
        self.mock_healthcheck_gateway.get_elasticsearch_health.return_value = {
            "status": "green"
        }

        response, status_code = self.get_healthcheck.get_service_health()

        self.assertEqual(status_code, 503)
        self.assertEqual(
            response,
            {
                "status": "fail",
                "description": "Health status of Explorer Service",
                "checks": {
                    "fullnode": [
                        {
                            "status": "fail",
                            "output": "Fullnode healthcheck errored: Unable to connect",
                            "componentName": "fullnode",
                            "componentType": "http",
                            "time": ANY,
                        }
                    ],
                    "wallet_service_db": [
                        {
                            "status": "pass",
                            "output": "Wallet service DB is healthy",
                            "componentName": "wallet_service_db",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "redis": [
                        {
                            "status": "pass",
                            "output": "Redis is healthy",
                            "componentName": "redis",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "elasticsearch": [
                        {
                            "status": "pass",
                            "output": "{'status': 'green'}",
                            "componentName": "elasticsearch",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                },
            },
        )

    def test_wallet_service_db_raises_exception(self):
        async def mock_get_hathor_core_version():
            return {"version": "0.38.0"}

        self.mock_healthcheck_gateway.get_hathor_core_version.side_effect = (
            mock_get_hathor_core_version
        )
        self.mock_healthcheck_gateway.ping_wallet_service_db.side_effect = Exception(
            "Unable to connect"
        )
        self.mock_healthcheck_gateway.ping_redis.return_value = True
        self.mock_healthcheck_gateway.get_elasticsearch_health.return_value = {
            "status": "green"
        }

        response, status_code = self.get_healthcheck.get_service_health()

        self.assertEqual(status_code, 503)
        self.assertEqual(
            response,
            {
                "status": "fail",
                "description": "Health status of Explorer Service",
                "checks": {
                    "fullnode": [
                        {
                            "status": "pass",
                            "output": "Fullnode is healthy",
                            "componentName": "fullnode",
                            "componentType": "http",
                            "time": ANY,
                        }
                    ],
                    "wallet_service_db": [
                        {
                            "status": "fail",
                            "output": "Wallet service DB healthcheck errored: Exception('Unable to connect')",
                            "componentName": "wallet_service_db",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "redis": [
                        {
                            "status": "pass",
                            "output": "Redis is healthy",
                            "componentName": "redis",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "elasticsearch": [
                        {
                            "status": "pass",
                            "output": "{'status': 'green'}",
                            "componentName": "elasticsearch",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                },
            },
        )

    def test_wallet_service_db_reports_unhealthy(self):
        async def mock_get_hathor_core_version():
            return {"version": "0.38.0"}

        self.mock_healthcheck_gateway.get_hathor_core_version.side_effect = (
            mock_get_hathor_core_version
        )
        self.mock_healthcheck_gateway.ping_wallet_service_db.return_value = (
            False,
            "Some MySQL Error message",
        )
        self.mock_healthcheck_gateway.ping_redis.return_value = True
        self.mock_healthcheck_gateway.get_elasticsearch_health.return_value = {
            "status": "green"
        }

        response, status_code = self.get_healthcheck.get_service_health()

        self.assertEqual(status_code, 503)
        self.assertEqual(
            response,
            {
                "status": "fail",
                "description": "Health status of Explorer Service",
                "checks": {
                    "fullnode": [
                        {
                            "status": "pass",
                            "output": "Fullnode is healthy",
                            "componentName": "fullnode",
                            "componentType": "http",
                            "time": ANY,
                        }
                    ],
                    "wallet_service_db": [
                        {
                            "status": "fail",
                            "output": "Wallet service DB didn't respond as expected: Some MySQL Error message",
                            "componentName": "wallet_service_db",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "redis": [
                        {
                            "status": "pass",
                            "output": "Redis is healthy",
                            "componentName": "redis",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "elasticsearch": [
                        {
                            "status": "pass",
                            "output": "{'status': 'green'}",
                            "componentName": "elasticsearch",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                },
            },
        )

    def test_redis_raises_exception(self):
        async def mock_get_hathor_core_version():
            return {"version": "0.38.0"}

        self.mock_healthcheck_gateway.get_hathor_core_version.side_effect = (
            mock_get_hathor_core_version
        )
        self.mock_healthcheck_gateway.ping_wallet_service_db.return_value = (True, "1")
        self.mock_healthcheck_gateway.ping_redis.side_effect = Exception(
            "Unable to connect"
        )
        self.mock_healthcheck_gateway.get_elasticsearch_health.return_value = {
            "status": "green"
        }

        response, status_code = self.get_healthcheck.get_service_health()

        self.assertEqual(status_code, 503)
        self.assertEqual(
            response,
            {
                "status": "fail",
                "description": "Health status of Explorer Service",
                "checks": {
                    "fullnode": [
                        {
                            "status": "pass",
                            "output": "Fullnode is healthy",
                            "componentName": "fullnode",
                            "componentType": "http",
                            "time": ANY,
                        }
                    ],
                    "wallet_service_db": [
                        {
                            "status": "pass",
                            "output": "Wallet service DB is healthy",
                            "componentName": "wallet_service_db",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "redis": [
                        {
                            "status": "fail",
                            "output": "Redis healthcheck errored: Exception('Unable to connect')",
                            "componentName": "redis",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "elasticsearch": [
                        {
                            "status": "pass",
                            "output": "{'status': 'green'}",
                            "componentName": "elasticsearch",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                },
            },
        )

    def test_redis_reports_unhealthy(self):
        async def mock_get_hathor_core_version():
            return {"version": "0.38.0"}

        self.mock_healthcheck_gateway.get_hathor_core_version.side_effect = (
            mock_get_hathor_core_version
        )
        self.mock_healthcheck_gateway.ping_wallet_service_db.return_value = (True, "1")
        self.mock_healthcheck_gateway.ping_redis.return_value = False
        self.mock_healthcheck_gateway.get_elasticsearch_health.return_value = {
            "status": "green"
        }

        response, status_code = self.get_healthcheck.get_service_health()

        self.assertEqual(status_code, 503)
        self.assertEqual(
            response,
            {
                "status": "fail",
                "description": "Health status of Explorer Service",
                "checks": {
                    "fullnode": [
                        {
                            "status": "pass",
                            "output": "Fullnode is healthy",
                            "componentName": "fullnode",
                            "componentType": "http",
                            "time": ANY,
                        }
                    ],
                    "wallet_service_db": [
                        {
                            "status": "pass",
                            "output": "Wallet service DB is healthy",
                            "componentName": "wallet_service_db",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "redis": [
                        {
                            "status": "fail",
                            "output": "Redis reported as unhealthy",
                            "componentName": "redis",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "elasticsearch": [
                        {
                            "status": "pass",
                            "output": "{'status': 'green'}",
                            "componentName": "elasticsearch",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                },
            },
        )

    def test_elasticsearch_raises_exception(self):
        async def mock_get_hathor_core_version():
            return {"version": "0.38.0"}

        self.mock_healthcheck_gateway.get_hathor_core_version.side_effect = (
            mock_get_hathor_core_version
        )
        self.mock_healthcheck_gateway.ping_wallet_service_db.return_value = (True, "1")
        self.mock_healthcheck_gateway.ping_redis.return_value = True
        self.mock_healthcheck_gateway.get_elasticsearch_health.side_effect = Exception(
            "Unable to connect"
        )

        response, status_code = self.get_healthcheck.get_service_health()

        self.assertEqual(status_code, 503)
        self.assertEqual(
            response,
            {
                "status": "fail",
                "description": "Health status of Explorer Service",
                "checks": {
                    "fullnode": [
                        {
                            "status": "pass",
                            "output": "Fullnode is healthy",
                            "componentName": "fullnode",
                            "componentType": "http",
                            "time": ANY,
                        }
                    ],
                    "wallet_service_db": [
                        {
                            "status": "pass",
                            "output": "Wallet service DB is healthy",
                            "componentName": "wallet_service_db",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "redis": [
                        {
                            "status": "pass",
                            "output": "Redis is healthy",
                            "componentName": "redis",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "elasticsearch": [
                        {
                            "status": "fail",
                            "output": "Elasticsearch healthcheck errored: Exception('Unable to connect')",
                            "componentName": "elasticsearch",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                },
            },
        )

    def test_elasticsearch_reports_unhealthy(self):
        async def mock_get_hathor_core_version():
            return {"version": "0.38.0"}

        self.mock_healthcheck_gateway.get_hathor_core_version.side_effect = (
            mock_get_hathor_core_version
        )
        self.mock_healthcheck_gateway.ping_wallet_service_db.return_value = (True, "1")
        self.mock_healthcheck_gateway.ping_redis.return_value = True
        self.mock_healthcheck_gateway.get_elasticsearch_health.return_value = {
            "status": "red"
        }

        response, status_code = self.get_healthcheck.get_service_health()

        self.assertEqual(status_code, 503)
        self.assertEqual(
            response,
            {
                "status": "fail",
                "description": "Health status of Explorer Service",
                "checks": {
                    "fullnode": [
                        {
                            "status": "pass",
                            "output": "Fullnode is healthy",
                            "componentName": "fullnode",
                            "componentType": "http",
                            "time": ANY,
                        }
                    ],
                    "wallet_service_db": [
                        {
                            "status": "pass",
                            "output": "Wallet service DB is healthy",
                            "componentName": "wallet_service_db",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "redis": [
                        {
                            "status": "pass",
                            "output": "Redis is healthy",
                            "componentName": "redis",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                    "elasticsearch": [
                        {
                            "status": "fail",
                            "output": "Elasticsearch is not healthy: {'status': 'red'}",
                            "componentName": "elasticsearch",
                            "componentType": "datastore",
                            "time": ANY,
                        }
                    ],
                },
            },
        )

    # @patch('your_module.HealthcheckGateway.get_hathor_core_version')
    # async def test_get_fullnode_health_failure(self, mock_get_version):
    #     mock_get_version.return_value = {"error": "Unable to connect"}

    #     result = await self.get_healthcheck._get_fullnode_health()

    #     self.assertEqual(result, HealthcheckCallbackResponse(status="fail", output="Fullnode healthcheck errored: Unable to connect"))
    #     mock_get_version.assert_called_once()
