from typing import Optional

from common.errors import HathorCoreTimeout
from gateways.node_api_gateway import NodeApiGateway

ADDRESS_BLACKLIST_RESPONSE = {
    'success': False,
    'message': 'Timeout due to too many transaction',
}


class NodeApi:
    def __init__(self, node_api_gateway: Optional[NodeApiGateway] = None) -> Optional[None]:
        self.node_api_gateway = node_api_gateway or NodeApiGateway()

    def get_address_balance(self, address: str) -> Optional[dict]:
        # check if blacklisted
        if self.node_api_gateway.is_blacklisted_address(address):
            return ADDRESS_BLACKLIST_RESPONSE

        try:
            return self.node_api_gateway.get_address_balance(address)
        except HathorCoreTimeout:
            self.node_api_gateway.blacklist_address(address)
            return ADDRESS_BLACKLIST_RESPONSE

    def get_address_search(
            self, address: str, count: int, page: Optional[str] = None,
            hash: Optional[str] = None, token: Optional[str] = None) -> Optional[dict]:
        # check if blacklisted
        if self.node_api_gateway.is_blacklisted_address(address):
            return ADDRESS_BLACKLIST_RESPONSE

        try:
            return self.node_api_gateway.get_address_search(
                    address,
                    count,
                    page,
                    hash,
                    token)
        except HathorCoreTimeout:
            self.node_api_gateway.blacklist_address(address)
            return ADDRESS_BLACKLIST_RESPONSE