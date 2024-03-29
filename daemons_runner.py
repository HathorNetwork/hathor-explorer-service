#!/usr/bin/env python3

import asyncio

from daemons.data_collector import DataCollector


async def data_collector() -> None:
    data_collector = DataCollector()
    while True:
        # This could take longer to run than the sleep time, so we wait for it to finish
        await data_collector.run()
        # Wait for 1 second before running again
        await asyncio.sleep(1)


def main() -> None:
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(data_collector())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()


if __name__ == "__main__":
    main()
