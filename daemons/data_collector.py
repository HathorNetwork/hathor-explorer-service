#!/usr/bin/env python3

import asyncio

from usecases.collect_nodes_statuses import CollectNodesStatuses
from common.logging import get_logger

logger = get_logger()

class DataCollector:
    async def run(self) -> None:
        await CollectNodesStatuses().collect()


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
