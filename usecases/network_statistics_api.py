from typing import Optional

from gateways.network_statistics_api_gateway import NetworkStatisticsApiGateway


class NetworkStatisticsApi:
    def __init__(
        self, network_statistics_api_gateway: Optional[NetworkStatisticsApiGateway] = None
    ) -> Optional[None]:
        self.network_statistics_api_gateway = (
            network_statistics_api_gateway or NetworkStatisticsApiGateway()
        )

    def get_basic_statistics() -> dict:
        result = self.network_statistics_api_gateway.get_basic_statistics()
        return result
