from typing import Optional, List

from domain.wallet_service import TokenBalance, TxHistoryEntry, TokenEntry
from gateways.clients.wallet_service_db_client import WalletServiceDBClient


class WalletServiceGateway:
    def __init__(self, db_client: Optional[WalletServiceDBClient] = None):
        self.db_client = db_client or WalletServiceDBClient()

    def address_balance(self, address: str, token: str) -> List[TokenBalance]:
        row = self.db_client.get_address_balance(address, token)
        return TokenBalance.from_row(row)

    def address_history(self, address: str, token: str, limit: int, skip: int) -> List[TxHistoryEntry]:
        rows = self.db_client.get_address_history(address, token, limit, skip)
        return [TxHistoryEntry.from_row(row) for row in rows]

    def address_tokens(self, address: str) -> List[TokenEntry]:
        rows = self.db_client.get_address_tokens(address)
        return [TokenEntry.from_row(row) for row in rows]
