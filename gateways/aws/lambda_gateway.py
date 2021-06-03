from typing import Union

from common.configuration import DATA_AGGREGATOR_LAMBDA_NAME
from domain.network.node import Node
from gateways.aws.lambda_client import LambdaClient


class LambdaGateway:
    """Gateway for AWS lambda comunications

    :param lambda_client: Client for lambda interactions, defaults to domain LambdaClient
    :type lambda_client:  :py:class:`gateways.aws.lambda_client.LambdaClient`, optional
    """
    def __init__(self, lambda_client: Union[LambdaClient, None] = None) -> None:
        self.lambda_client = lambda_client or LambdaClient()

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

        raise Exception('No lambda name in config')
