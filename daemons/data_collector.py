#!/usr/bin/env python3

import asyncio
from typing import Optional

from common.configuration import HEALTHCHECK_PING_ENABLED
from common.logging import get_logger
from usecases.collect_nodes_statuses import CollectNodesStatuses
from utils.healthcheck.healthcheck_ping_manager import HealthcheckPingManager

logger = get_logger()


class DataCollector:
    def __init__(
        self, healthcheck_ping_manager: Optional[HealthcheckPingManager] = None
    ) -> None:
        if not healthcheck_ping_manager and HEALTHCHECK_PING_ENABLED:
            healthcheck_ping_manager = HealthcheckPingManager()

        self.healthcheck_ping_manager = healthcheck_ping_manager

    async def run(self) -> None:
        await CollectNodesStatuses().collect()
        if self.healthcheck_ping_manager:
            # This sends a ping to the configured healthcheck service (if any)
            await self.healthcheck_ping_manager.send_ping("data_collector")


def main() -> None:
    log = logger.new()
    log.info("Starting DataCollector")
    loop = asyncio.get_event_loop()
    try:
        data_collector = DataCollector()
        asyncio.ensure_future(data_collector.run())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Closing DataCollector loop")
        loop.close()


if __name__ == "__main__":
    main()
