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
DECODE_TX_ENDPOINT = '/v1a/decode_tx'
PUSH_TX_ENDPOINT = '/v1a/push_tx'
GRAPHVIZ_DOT_NEIGHBORS_ENDPOINT = '/v1a/graphviz/neighbours.dot/'
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
        self.log = logger.new(client="async")

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
                    self.log.info(
                        "hathor_core_response",
                        path=path,
                        status=response.status,
                        body=await response.text())
                    callback(await response.json())
        except Exception as e:
            self.log.error("hathor_core_error", path=path, error=repr(e))
            callback({'error': repr(e)})


class HathorCoreClient:
    """Client to make requests

    :param domain: domain where the requests will be made, defaults to config `hathor_core_domain`
    :type domain: str, optional
    """
    def __init__(self, domain: Optional[str] = None) -> None:
        self.domain = domain or HATHOR_CORE_DOMAIN
        self.log = logger.new(client="sync")

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
                self.log.warning(
                        "hathor_core_error",
                        path=path,
                        status=response.status_code,
                        body=response.text)
                return None
            self.log.info(
                    "hathor_core_response",
                    path=path,
                    status=response.status_code,
                    body=response.text)

            return response.json()
        except requests.ReadTimeout:
            self.log.error("hathor_core_error", error="timeout", path=path)
            raise HathorCoreTimeout('timeout')
        except Exception as e:
            self.log.error("hathor_core_error", error=repr(e), path=path)
            return {'error': repr(e)}
