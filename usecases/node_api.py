from typing import List, Optional

from common.errors import HathorCoreTimeout
from gateways.node_api_gateway import NodeApiGateway

ADDRESS_BLACKLIST_RESPONSE = {
    "success": False,
    "message": "Timeout due to too many transaction",
}


class NodeApi:
    def __init__(
        self, node_api_gateway: Optional[NodeApiGateway] = None
    ) -> Optional[None]:
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
        self,
        address: str,
        count: int,
        page: Optional[str] = None,
        hash: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[dict]:
        # check if blacklisted
        if self.node_api_gateway.is_blacklisted_address(address):
            return ADDRESS_BLACKLIST_RESPONSE

        try:
            return self.node_api_gateway.get_address_search(
                address, count, page, hash, token
            )
        except HathorCoreTimeout:
            self.node_api_gateway.blacklist_address(address)
            return ADDRESS_BLACKLIST_RESPONSE

    def get_version(self) -> Optional[dict]:
        return self.node_api_gateway.get_version()

    def get_feature(self, block: Optional[str]) -> Optional[dict]:
        return self.node_api_gateway.get_feature(block)

    def get_dashboard_tx(self, block: int, tx: int) -> Optional[dict]:
        return self.node_api_gateway.get_dashboard_tx(block, tx)

    def get_transaction_acc_weight(self, id: str) -> Optional[dict]:
        return self.node_api_gateway.get_transaction_acc_weight(id)

    def get_token_history(
        self,
        id: str,
        count: int,
        hash: Optional[str] = None,
        page: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> Optional[dict]:
        return self.node_api_gateway.get_token_history(id, count, hash, page, timestamp)

    def get_transaction(self, id: str) -> Optional[dict]:
        return self.node_api_gateway.get_transaction(id)

    def decode_tx(self, hex_tx: str) -> Optional[dict]:
        return self.node_api_gateway.decode_tx(hex_tx)

    def push_tx(self, hex_tx: str) -> Optional[dict]:
        return self.node_api_gateway.push_tx(hex_tx)

    def graphviz_dot_neighbors(
        self, tx: str, graph_type: str, max_level: int
    ) -> Optional[str]:
        return self.node_api_gateway.graphviz_dot_neighbors(tx, graph_type, max_level)

    def list_transactions(
        self,
        type: str,
        count: int,
        hash: Optional[str] = None,
        page: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> Optional[dict]:
        return self.node_api_gateway.list_transactions(
            type, count, hash, page, timestamp
        )

    def get_token(self, id: str) -> Optional[dict]:
        return self.node_api_gateway.get_token(id)

    def get_nc_state(
        self, id: str, fields: List[str], balances: List[str], calls: List[str]
    ) -> Optional[dict]:
        return self.node_api_gateway.get_nc_state(id, fields, balances, calls)

    def get_nc_history(
        self,
        id: str,
        after: Optional[str] = None,
        before: Optional[str] = None,
        count: Optional[int] = None,
    ) -> Optional[dict]:
        return self.node_api_gateway.get_nc_history(id, after, before, count)

    def get_nc_blueprint_information(self, blueprint_id: str) -> Optional[dict]:
        return self.node_api_gateway.get_nc_blueprint_information(blueprint_id)

    def get_nc_blueprint_source_code(self, blueprint_id: str) -> Optional[dict]:
        return self.node_api_gateway.get_nc_blueprint_source_code(blueprint_id)

    def get_nc_builtin_blueprints(
        self,
        after: Optional[str] = None,
        before: Optional[str] = None,
        count: Optional[int] = None,
        find_blueprint_id: Optional[str] = None,
        find_blueprint_name: Optional[str] = None,
    ) -> Optional[dict]:
        return self.node_api_gateway.get_nc_builtin_blueprints(
            after, before, count, find_blueprint_id, find_blueprint_name
        )

    def get_nc_on_chain_blueprints(
        self,
        after: Optional[str] = None,
        before: Optional[str] = None,
        count: Optional[int] = None,
        find_blueprint_id: Optional[str] = None,
        find_blueprint_name: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Optional[dict]:
        return self.node_api_gateway.get_nc_on_chain_blueprints(
            after, before, count, find_blueprint_id, find_blueprint_name, order
        )

    def get_nc_creation_list(
        self,
        after: Optional[str] = None,
        before: Optional[str] = None,
        count: Optional[int] = None,
        find_nano_contract_id: Optional[str] = None,
        find_blueprint_id: Optional[str] = None,
        find_blueprint_name: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Optional[dict]:
        return self.node_api_gateway.get_nc_creation_list(
            after, before, count, find_nano_contract_id, find_blueprint_id, find_blueprint_name, order
        )
