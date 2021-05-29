from typing import Union

from common import config
from domain.network.network import Network
from gateways.aws.lambda_client import LambdaClient


class LambdaGateway:
    """Gateway for AWS lambda comunications

    :param lambda_client: Client for lambda interactions, defaults to domain LambdaClient
    :type lambda_client:  :py:class:`gateways.aws.lambda_client.LambdaClient`, optional
    """
    def __init__(self, lambda_client: Union[LambdaClient, None] = None) -> None:
        self.lambda_client = lambda_client or LambdaClient()

    def send_network_to_data_aggregator(self, payload: Network) -> int:
        """Invoke data-aggregator lambda passing network data to be aggregated

        :param payload: Network data to be sent
        :type payload: :py:class:`domain.network.network.Network`
        :return: Status code of the request
        :rtype: int
        """
        lambda_name = config.data_aggregator_lambda_name

        if lambda_name is not None:
            return self.lambda_client.invoke_async(lambda_name, payload.to_dict())

        raise Exception('No lambda name in config')
