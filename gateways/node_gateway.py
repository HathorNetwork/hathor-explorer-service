from typing import Callable, List, Union

from common.configuration import DATA_AGGREGATOR_LAMBDA_NAME, NODE_CACHE_TTL
from common.errors import ConfigError
from domain.network.node import Node
from gateways.clients.cache_client import NODE_COLLECTION_NAME, CacheClient
from gateways.clients.hathor_core_client import STATUS_ENDPOINT, HathorCoreAsyncClient
from gateways.clients.lambda_client import LambdaClient


class NodeGateway:
    """Gateway for Node actions

    :param hathor_core_async_client: Hathor Core client for api calls, defaults to HathorCoreAsyncClient
    :type hathor_core_async_client: Union[HathorCoreAsyncClient, None], optional
    :param cache_client: Cache Client for cache manipulation, defaults to CacheClient
    :type cache_client: Union[CacheClient, None], optional
    :param lambda_client: lambda client for lambda invocations, defaults to LambdaClient
    :type lambda_client: Union[LambdaClient, None], optional
    """
    def __init__(
        self,
        hathor_core_async_client: Union[HathorCoreAsyncClient, None] = None,
        cache_client: Union[CacheClient, None] = None,
        lambda_client: Union[LambdaClient, None] = None
    ) -> None:
        self.hathor_core_async_client = hathor_core_async_client or HathorCoreAsyncClient()
        self.cache_client = cache_client or CacheClient()
        self.lambda_client = lambda_client or LambdaClient()

    async def get_node_status_async(self, callback: Callable[[dict], None]) -> None:
        """Retrieve status from full-node

        :param callback: method to be called passing response as param
        :type callback: Callable[[dict], None]
        """
        await self.hathor_core_async_client.get(STATUS_ENDPOINT, callback)

    def send_node_to_data_aggregator(self, payload: Node) -> int:
        """Invoke data-aggregator lambda passing node data to be aggregated

        :param payload: Node data to be sent
        :type payload: :py:class:`domain.network.node.Node`
        :return: Status code of the request
        :rtype: int
        """
        lambda_name = DATA_AGGREGATOR_LAMBDA_NAME

        if lambda_name is not None:
            return self.lambda_client.invoke_async(lambda_name, payload.to_dict())

        raise ConfigError('No lambda name in config')

    def save_node(self, id: str, node: Node) -> Union[bool, None]:
        """Saves Node data into cache with id as key

        :param id: identifier for the data
        :type id: str
        :param node: Node object with data
        :type node: :py:class:`domain.network.node.Node`
        :return: If saved successfuly or not
        :rtype: bool
        """
        return self.cache_client.set(NODE_COLLECTION_NAME, id, node.to_dict(), NODE_CACHE_TTL)

    def get_node(self, id: str) -> Union[Node, None]:
        """Retrives node data for given id

        :param id: data identifier
        :type id: str
        :return: Node data or None if nothing found
        :rtype: Union[Node, None]
        """
        value = self.cache_client.get(NODE_COLLECTION_NAME, id)

        if value is not None:
            return Node.from_dict(value)

        return None

    def list_node_keys(self) -> List[str]:
        """List current ids of saved nodes

        :return: list of ids
        :rtype: List[str]
        """
        return self.cache_client.keys(NODE_COLLECTION_NAME)
