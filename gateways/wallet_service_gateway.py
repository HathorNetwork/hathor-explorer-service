from typing import List, Optional, Tuple

from domain.wallet_service import TokenBalance, TokenEntry, TxHistoryEntry
from gateways.clients.wallet_service_db_client import WalletServiceDBClient


class WalletServiceGateway:
    def __init__(self, db_client: Optional[WalletServiceDBClient] = None):
        self.db_client = db_client or WalletServiceDBClient()

    def address_balance(self, address: str, token: str) -> TokenBalance:
        """ Fetch the balance of a token on a particular address."""
        balance = self.db_client.get_address_balance(address, token)
        return TokenBalance.from_dict(balance)

    def address_history(self, address: str, token: str, limit: int, offset: int) -> List[TxHistoryEntry]:
        """ Fetch the tx history for an address/token pair, paginated."""
        history = self.db_client.get_address_history(address, token, limit, offset)
        return [TxHistoryEntry.from_dict(tx) for tx in history]

    def address_tokens(self, address: str, limit: int, offset: int) -> Tuple[int, List[TokenEntry]]:
        """ Fetch the tokens on the address history, paginated

        Returns the total number of different tokens and a list of tokens found.
        """
        tokens = self.db_client.get_address_tokens(address, limit, offset)
        total: int = tokens[0]['total'] if len(tokens) > 0 else 0

        return total, [TokenEntry.from_dict(token) for token in tokens]
