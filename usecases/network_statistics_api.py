from typing import Optional

from elasticsearch import exceptions

from common.errors import ApiError
from common.logging import get_logger
from gateways.network_statistics_api_gateway import NetworkStatisticsApiGateway

logger = get_logger()


class NetworkStatisticsApi:
    def __init__(
        self,
        network_statistics_api_gateway: Optional[NetworkStatisticsApiGateway] = None,
    ) -> Optional[None]:
        self.network_statistics_api_gateway = (
            network_statistics_api_gateway or NetworkStatisticsApiGateway()
        )

    def get_basic_statistics(self) -> dict:
        try:
            return self.network_statistics_api_gateway.get_transaction_statistics()
        except exceptions.ApiError as err:
            logger.error(
                "ExplorerService failed to fetch transaction statistics from ElasticSearch"
            )
            raise ApiError("gateway_error")
        except exceptions.TransportError:
            logger.error("ElasticSearch transport error")
            raise ApiError("internal_error")
