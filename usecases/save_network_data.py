from domain.network.network import Network
from gateways.cache.cache_gateway import CacheGateway


class SaveNetworkData:

    def __init__(self, cache_gateway: CacheGateway = None) -> None:
        self.cache_gateway = cache_gateway or CacheGateway()

    def save(self, payload: dict) -> bool:
        network = Network.from_dict(payload)
        return self.cache_gateway.save_network(network.id, network)
