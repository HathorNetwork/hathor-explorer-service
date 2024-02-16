import asyncio
from typing import Any, Dict, Optional, Tuple

from healthcheck import (
    Healthcheck,
    HealthcheckCallbackResponse,
    HealthcheckDatastoreComponent,
    HealthcheckHTTPComponent,
    HealthcheckStatus,
)

from common.configuration import (
    HEALTHCHECK_ELASTICSEARCH_ENABLED,
    HEALTHCHECK_HATHOR_CORE_ENABLED,
    HEALTHCHECK_REDIS_ENABLED,
    HEALTHCHECK_WALLET_SERVICE_DB_ENABLED,
)
from gateways.healthcheck_gateway import HealthcheckGateway


class GetHealthcheck:
    def __init__(
        self,
        healthcheck: Optional[Healthcheck] = None,
        healthcheck_gateway: Optional[HealthcheckGateway] = None,
    ):
        self.healthcheck = healthcheck or Healthcheck(
            "Explorer Service", warn_is_unhealthy=True
        )
        self.healthcheck_gateway = healthcheck_gateway or HealthcheckGateway()

        self.components = {}

        if HEALTHCHECK_HATHOR_CORE_ENABLED:
            self.components["fullnode"] = HealthcheckHTTPComponent(
                name="fullnode"
            ).add_healthcheck(self._get_fullnode_health)

        if HEALTHCHECK_WALLET_SERVICE_DB_ENABLED:
            self.components["wallet_service_db"] = HealthcheckDatastoreComponent(
                name="wallet_service_db"
            ).add_healthcheck(self._get_wallet_service_db_health)

        if HEALTHCHECK_REDIS_ENABLED:
            self.components["redis"] = HealthcheckDatastoreComponent(
                name="redis"
            ).add_healthcheck(self._get_redis_health)

        if HEALTHCHECK_ELASTICSEARCH_ENABLED:
            self.components["elasticsearch"] = HealthcheckDatastoreComponent(
                name="elasticsearch"
            ).add_healthcheck(self._get_elasticsearch_health)

        for component in self.components.values():
            self.healthcheck.add_component(component)

    async def _get_fullnode_health(self):
        health_response = await self.healthcheck_gateway.get_hathor_core_health()

        if "error" in health_response:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.FAIL,
                output=f"Fullnode healthcheck errored: {health_response['error']}",
            )

        status = health_response["status"]

        # Here we're assuming that a 'warn' status will be considered as unhealthy
        is_healthy = status == HealthcheckStatus.PASS
        is_unhealthy = status in [HealthcheckStatus.FAIL, HealthcheckStatus.WARN]

        if is_unhealthy:
            output = f"Fullnode is not healthy: {str(health_response)}"
        elif is_healthy:
            output = "Fullnode is healthy"
        else:
            status = HealthcheckStatus.FAIL
            output = (
                f"Fullnode returned an unexpected health status: {str(health_response)}"
            )

        return HealthcheckCallbackResponse(
            status=status,
            output=output,
        )

    async def _get_wallet_service_db_health(self):
        try:
            is_healthy, output = self.healthcheck_gateway.ping_wallet_service_db()
        except Exception as e:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.FAIL,
                output=f"Wallet service DB healthcheck errored: {repr(e)}",
            )

        return HealthcheckCallbackResponse(
            status=HealthcheckStatus.PASS if is_healthy else HealthcheckStatus.FAIL,
            output="Wallet service DB is healthy"
            if is_healthy
            else f"Wallet service DB didn't respond as expected: {output}",
        )

    async def _get_redis_health(self):
        try:
            is_healthy = self.healthcheck_gateway.ping_redis()
        except Exception as e:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.FAIL,
                output=f"Redis healthcheck errored: {repr(e)}",
            )

        return HealthcheckCallbackResponse(
            status=HealthcheckStatus.PASS if is_healthy else HealthcheckStatus.FAIL,
            output="Redis is healthy" if is_healthy else "Redis reported as unhealthy",
        )

    async def _get_elasticsearch_health(self):
        try:
            elasticsearch_info = self.healthcheck_gateway.get_elasticsearch_health()
        except Exception as e:
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.FAIL,
                output=f"Elasticsearch healthcheck errored: {repr(e)}",
            )

        if elasticsearch_info["status"] == "red":
            return HealthcheckCallbackResponse(
                status=HealthcheckStatus.FAIL,
                output=f"Elasticsearch is not healthy: {str(elasticsearch_info)}",
            )
        if elasticsearch_info["status"] == "yellow":
            return HealthcheckCallbackResponse(
                status="warn",
                output=f"Elasticsearch has warnings: {str(elasticsearch_info)}",
            )

        return HealthcheckCallbackResponse(
            status=HealthcheckStatus.PASS,
            output=str(elasticsearch_info),
        )

    def get_service_health(self) -> Tuple[Dict[str, Any], int]:
        response = asyncio.run(self.healthcheck.run())

        return response.to_json(), response.get_http_status_code()
