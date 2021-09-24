from typing import Optional

from gateways.node_api_gateway import NodeApiGateway


class NodeApi:
    def __init__(self, node_api_gateway: Optional[NodeApiGateway] = None) -> None:
        self.node_api_gateway = node_api_gateway or NodeApiGateway()

    def get_address_balance(self, address: str) -> dict:
        # check if blacklisted
        if self.node_api_gateway.is_blacklist_address_balance(address):
            return {'status': False, 'message': 'address blacklisted'}

        try:
            result = self.node_api_gateway.get_address_balance(address)
            return result.to_dict()
        except Exception as ex:
            if str(ex) == 'timeout':
                # blacklist address
                self.blacklist_address_balance(address)
                return {'status': False, 'message': 'address blacklisted'}
            raise ex

    def get_address_search(self, address: str, count: int, page: str, hash: str, token: Optional[str] = None) -> dict:
        # check if blacklisted
        if self.node_api_gateway.is_blacklist_address_search(address):
            return {'status': False, 'message': 'address blacklisted'}

        try:
            result = self.node_api_gateway.get_address_search(
                    address,
                    count,
                    page,
                    hash,
                    token)
            return result.to_dict()
        except Exception as ex:
            if str(ex) == 'timeout':
                # blacklist address
                self.blacklist_address_search(address)
                return {'status': False, 'message': 'address blacklisted'}
            raise ex
