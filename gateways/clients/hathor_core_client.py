from typing import Any, Callable, Optional
from urllib import parse

import aiohttp
import requests

from common.configuration import HATHOR_CORE_DOMAIN
from common.errors import HathorCoreTimeout
from common.logging import get_logger

logger = get_logger()

ADDRESS_BALANCE_ENDPOINT = '/v1a/thin_wallet/address_balance'
ADDRESS_SEARCH_ENDPOINT = '/v1a/thin_wallet/address_search'
DASHBOARD_TX_ENDPOINT = '/v1a/dashboard_tx'
STATUS_ENDPOINT = '/v1a/status'
TOKEN_ENDPOINT = '/v1a/thin_wallet/token'
TOKEN_HISTORY_ENDPOINT = '/v1a/thin_wallet/token_history'
TRANSACTION_ENDPOINT = '/v1a/transaction'
TX_ACC_WEIGHT_ENDPOINT = '/v1a/transaction_acc_weight'
VERSION_ENDPOINT = '/v1a/version'


class HathorCoreAsyncClient:

    def __init__(self, domain: Optional[str] = None) -> None:
        """Client to make async requests

        :param domain: domain where the requests will be made, defaults to config `hathor_core_domain`
        :type domain: str, optional
        """
        self.domain = domain or HATHOR_CORE_DOMAIN

    async def get(self, path: str, callback: Callable[[dict], None], params: Optional[dict] = None) -> None:
        """Make a get request async

        :param path: path to be requested
        :type path: str
        :param callback: callback to be called with the response as argument
        :type callback: Callable[[dict], None]
        :param params: params to be sent
        :type params: Optional[dict]
        """
        url = parse.urljoin(f"https://{self.domain}", path)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    callback(await response.json())
        except Exception as e:
            callback({'error': repr(e)})


class HathorCoreClient:
    """Client to make requests

    :param domain: domain where the requests will be made, defaults to config `hathor_core_domain`
    :type domain: str, optional
    """
    def __init__(self, domain: Optional[str] = None) -> None:
        self.domain = domain or HATHOR_CORE_DOMAIN

    def get(self, path: str, params: Optional[dict] = None, **kwargs: Any) -> Optional[dict]:
        """Make a get request

        :param path: path to be requested
        :type path: str
        :param params: params to be sent
        :type params: Optional[dict]
        :param **kwargs: kwargs for `requests.get`
        :type **kwargs: Any
        :return: request response
        :rtype: Optional[dict]
        """
        url = parse.urljoin(f"https://{self.domain}", path)

        try:
            response = requests.get(url, params=params, **kwargs)
            if response.status_code != 200:
                logger.warning(f'Hathor Core Unexpected response ({response.status_code}): {response.text}')
                return None

            return response.json()
        except requests.ReadTimeout:
            raise HathorCoreTimeout('timeout')
        except Exception as e:
            return {'error': repr(e)}
