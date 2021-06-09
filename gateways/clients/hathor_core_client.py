from typing import Callable, Union
from urllib import parse

import aiohttp
import requests

from common.configuration import HATHOR_CORE_DOMAIN

STATUS_ENDPOINT = '/v1a/status'
TOKEN_ENDPOINT = '/v1a/thin_wallet/token'


class HathorCoreAsyncClient:

    def __init__(self, domain: Union[str, None] = None) -> None:
        """Client to make async requests

        :param domain: domain where the requests will be made, defaults to config `hathor_core_domain`
        :type domain: str, optional
        """
        self.domain = domain or HATHOR_CORE_DOMAIN

    async def get(self, path: str, callback: Callable[[dict], None]) -> None:
        """Make a get request async

        :param path: path to be requested
        :type path: str
        :param callback: callback to be called with the response as argument
        :type callback: Callable[[dict], None]
        """
        url = parse.urljoin(f"https://{self.domain}", path)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    callback(await response.json())
        except Exception as e:
            callback({'error': repr(e)})


class HathorCoreClient:
    """Client to make requests

    :param domain: domain where the requests will be made, defaults to config `hathor_core_domain`
    :type domain: str, optional
    """
    def __init__(self, domain: Union[str, None] = None) -> None:
        self.domain = domain or HATHOR_CORE_DOMAIN

    def get(self, path: str, params: dict = {}) -> Union[dict, None]:
        """Make a get request

        :param path: path to be requested
        :type path: str
        :param params: params to be sent
        :type params: dict, optional
        :return: request response
        :rtype: Union[dict, None]
        """
        url = parse.urljoin(f"https://{self.domain}", path)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return None

            return response.json()
        except Exception as e:
            return {'error': repr(e)}
