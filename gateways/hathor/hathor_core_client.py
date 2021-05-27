from typing import Callable, Union
from urllib import parse

import aiohttp

from common import config


class HathorCoreClient:

    def __init__(self, domain: Union[str, None] = None) -> None:
        self.domain = domain or config.hathor_core_domain

    def get(self, path: str) -> dict:
        return {}


class HathorCoreAsyncClient:

    def __init__(self, domain: Union[str, None] = None) -> None:
        """Client to make async requests

        :param domain: domain where the requests will be made, defaults to config `hathor_core_domain`
        :type domain: str, optional
        """
        self.domain = domain or config.hathor_core_domain
        self.session = aiohttp.ClientSession()

    async def get(self, path: str, callback: Callable[[dict], None]) -> None:
        """Make a get request async

        :param path: path to be requested
        :type path: str
        :param callback: callback to be called with the response as argument
        :type callback: Callable[[dict], None]
        """
        url = parse.urljoin(f"https://{self.domain}", path)

        try:
            async with self.session as session:
                async with session.get(url) as response:
                    callback(await response.json())
        except Exception as e:
            callback({'error': repr(e)})
