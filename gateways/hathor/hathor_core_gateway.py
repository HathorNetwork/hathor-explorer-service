from typing import Callable

from gateways.hathor.hathor_core_client import HathorCoreClient, HathorCoreAsyncClient


class HathorCoreGateway:

    def __init__(self, client: HathorCoreClient = None, async_client: HathorCoreAsyncClient = None) -> None:
        self.client = client or HathorCoreClient()
        self.async_client = async_client or HathorCoreAsyncClient()

    async def get_async(self, path: str, callback: Callable[[dict], None]) -> None:
        await self.async_client.get(path, callback)
    
    def get(self, path: str) -> dict:
        return self.client.get(path)
