from typing import Callable, Union

from gateways.hathor.hathor_core_client import HathorCoreAsyncClient


class HathorCoreGateway:

    def __init__(
        self,
        async_client: Union[HathorCoreAsyncClient, None] = None
    ) -> None:
        self.async_client = async_client or HathorCoreAsyncClient()

    async def get_async(self, path: str, callback: Callable[[dict], None]) -> None:
        await self.async_client.get(path, callback)
