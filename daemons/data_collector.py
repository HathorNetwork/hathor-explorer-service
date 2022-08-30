#!/usr/bin/env python3

import asyncio

from usecases.collect_nodes_statuses import CollectNodesStatuses


class DataCollector:
    async def run(self) -> None:
        await CollectNodesStatuses().collect()


def main() -> None:
    loop = asyncio.get_event_loop()
    try:
        data_collector = DataCollector()
        asyncio.ensure_future(data_collector.run())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()


if __name__ == "__main__":
    main()
