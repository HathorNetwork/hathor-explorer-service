from typing import Optional

from gateways.node_api_gateway import NodeApiGateway


class NodeApi:
    def __init__(self, node_api_gateway: Optional[NodeApiGateway] = None) -> None:
        self.node_api_gateway = node_api_gateway or NodeApiGateway()

    def get_address_balance(self, address: str) -> dict:
        try:
            result = self.node_api_gateway.get_address_balance(address)
            return result.to_dict()
        except Exception as ex:
            if str(ex) == 'timeout':
                # blacklist address
                self.blacklist_address_balance(address)
                return {'status': False, 'message': 'address blacklisted'}
            raise ex
