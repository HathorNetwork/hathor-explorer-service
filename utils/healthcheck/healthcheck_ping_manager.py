from datetime import datetime

import aiohttp

from common.configuration import (
    HEALTHCHECK_DATA_COLLECTOR_URL,
    HEALTHCHECK_PING_ENABLED,
    HEALTHCHECK_PING_INTERVAL,
    HEALTHCHECK_SERVICE_API_KEY,
)
from common.logging import get_logger

logger = get_logger()


class HealthcheckPingManager:
    def __init__(self) -> None:
        self.targets = {
            "data_collector": {
                "interval": HEALTHCHECK_PING_INTERVAL,
                "url": HEALTHCHECK_DATA_COLLECTOR_URL,
                "latest_ping": None,
            }
        }

    async def _send_post(self, url: str) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-Api-Key": HEALTHCHECK_SERVICE_API_KEY,
                    "Content-Type": "application/json",
                }

                async with session.post(url, headers=headers) as response:
                    if response.status > 299:
                        data = await response.text()
                        logger.warning(
                            f"Failed sending ping to {url}",
                            status=response.status,
                            data=data,
                        )
        except Exception as e:
            logger.warning(f"Failed sending ping to {url}", failure=repr(e))

    async def send_ping(self, target: str) -> None:
        if not HEALTHCHECK_PING_ENABLED:
            return

        if target not in self.targets:
            raise ValueError(f"Invalid target: {target}")

        target_data = self.targets[target]

        if (
            target_data["latest_ping"] is None
            or (datetime.now() - target_data["latest_ping"]).total_seconds()
            >= target_data["interval"]
        ):
            target_data["latest_ping"] = datetime.now()

            await self._send_post(target_data["url"])
