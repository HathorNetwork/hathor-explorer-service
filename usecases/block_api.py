from typing import Optional

from gateways.block_api_gateway import BlockApiGateway


class BlockApi:
    def __init__(self, block_api_gateway: Optional[BlockApiGateway] = None) -> Optional[None]:
        self.block_api_gateway = block_api_gateway or BlockApiGateway()

    def get_best_chain_height(self) -> dict:
        return self.block_api_gateway.get_best_chain_height()
