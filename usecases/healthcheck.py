import asyncio
from typing import Any, Dict, Optional, Tuple

from healthcheck import (
    Healthcheck,
    HealthcheckCallbackResponse,
    HealthcheckDatastoreComponent,
    HealthcheckHTTPComponent,
)

from gateways.healthcheck_gateway import HealthcheckGateway


class GetHealthcheck:
    def __init__(
        self,
        healthcheck: Healthcheck = None,
        healthcheck_gateway: Optional[HealthcheckGateway] = None,
    ):
        self.healthcheck = healthcheck or Healthcheck("Explorer Service")
        self.healthcheck_gateway = healthcheck_gateway or HealthcheckGateway()

        self.components = {
            "fullnode": HealthcheckHTTPComponent(name="fullnode").add_healthcheck(
                self._get_fullnode_health
            ),
            "wallet_service_db": HealthcheckDatastoreComponent(
                name="wallet_service_db"
            ).add_healthcheck(self._get_wallet_service_db_health),
            "redis": HealthcheckDatastoreComponent(name="redis").add_healthcheck(
                self._get_redis_health
            ),
            "elasticsearch": HealthcheckDatastoreComponent(
                name="elasticsearch"
            ).add_healthcheck(self._get_elasticsearch_health),
        }

        for component in self.components.values():
            self.healthcheck.add_component(component)

    async def _get_fullnode_health(self):
        # TODO: We need to use the hathor-core's /health endpoint when it's available
        version_response = await self.healthcheck_gateway.get_hathor_core_version()

        if "error" in version_response:
            return HealthcheckCallbackResponse(
                status="fail",
                output=f"Fullnode healthcheck errored: {version_response['error']}",
            )

        return HealthcheckCallbackResponse(
            status="pass",
            output="Fullnode is healthy",
        )

    async def _get_wallet_service_db_health(self):
        try:
            is_healthy, output = self.healthcheck_gateway.ping_wallet_service_db()
        except Exception as e:
            return HealthcheckCallbackResponse(
                status="fail",
                output=f"Wallet service DB healthcheck errored: {repr(e)}",
            )

        return HealthcheckCallbackResponse(
            status="pass" if is_healthy else "fail",
            output="Wallet service DB is healthy"
            if is_healthy
            else f"Wallet service DB didn't respond as expected: {output}",
        )

    async def _get_redis_health(self):
        try:
            is_healthy = self.healthcheck_gateway.ping_redis()
        except Exception as e:
            return HealthcheckCallbackResponse(
                status="fail",
                output=f"Redis healthcheck errored: {repr(e)}",
            )

        return HealthcheckCallbackResponse(
            status="pass" if is_healthy else "fail",
            output="Redis is healthy" if is_healthy else "Redis reported as unhealthy",
        )

    async def _get_elasticsearch_health(self):
        try:
            elasticsearch_info = self.healthcheck_gateway.get_elasticsearch_health()
        except Exception as e:
            return HealthcheckCallbackResponse(
                status="fail",
                output=f"Elasticsearch healthcheck errored: {repr(e)}",
            )

        if elasticsearch_info["status"] == "red":
            return HealthcheckCallbackResponse(
                status="fail",
                output=f"Elasticsearch is not healthy: {str(elasticsearch_info)}",
            )
        if elasticsearch_info["status"] == "yellow":
            return HealthcheckCallbackResponse(
                status="warn",
                output=f"Elasticsearch has warnings: {str(elasticsearch_info)}",
            )

        return HealthcheckCallbackResponse(
            status="pass",
            output=str(elasticsearch_info),
        )

    def get_service_health(self) -> Tuple[Dict[str, Any], int]:
        response = asyncio.run(self.healthcheck.run())

        return response.to_json(), response.get_http_status_code()
