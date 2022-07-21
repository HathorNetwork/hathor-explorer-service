from typing import List, Optional

from domain.wallet_service import TokenBalance, TokenEntry, TxHistoryEntry
from gateways.clients.wallet_service_db_client import WalletServiceDBClient


class WalletServiceGateway:
    def __init__(self, db_client: Optional[WalletServiceDBClient] = None):
        self.db_client = db_client or WalletServiceDBClient()

    def address_balance(self, address: str, token: str) -> TokenBalance:
        balance = self.db_client.get_address_balance(address, token)
        return TokenBalance.from_dict(balance)

    def address_history(self, address: str, token: str, limit: int, skip: int) -> List[TxHistoryEntry]:
        history = self.db_client.get_address_history(address, token, limit, skip)
        return [TxHistoryEntry.from_dict(tx) for tx in history]

    def address_tokens(self, address: str) -> List[TokenEntry]:
        tokens = self.db_client.get_address_tokens(address)
        return [TokenEntry.from_dict(token) for token in tokens]
