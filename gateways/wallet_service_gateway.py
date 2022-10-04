from typing import List, Optional, Tuple

from domain.wallet_service import TokenBalance, TokenEntry, TxHistoryEntry
from gateways.clients.wallet_service_db_client import WalletServiceDBClient


class WalletServiceGateway:

    def __init__(self, db_client: Optional[WalletServiceDBClient] = None):
        self.db_client = db_client or WalletServiceDBClient()

    def address_balance(self, address: str, token: str) -> TokenBalance:
        """Fetch the balance of a token on a particular address."""
        balance = self.db_client.get_address_balance(address, token)
        return TokenBalance.from_dict(balance)

    def address_history(self,
                        address: str,
                        token: str,
                        limit: int,
                        last_tx: str,
                        last_ts: int) -> dict:
        """ Fetch the tx history for an address/token pair, paginated."""
        history = self.db_client.get_address_history(address, token, limit,
                                                     last_tx, last_ts)

        has_next = False
        has_previous = False

        if len(history) > 0:
            has_next = bool(history[0]['has_next'])
            has_previous = bool(history[0]['has_previous'])

        tx_history = [TxHistoryEntry.from_dict(tx) for tx in history]

        return {
            "has_next": has_next,
            "has_previous": has_previous,
            "history": tx_history
        }

    def address_tokens(
        self, address: str, limit: int, offset: int
    ) -> Tuple[int, List[TokenEntry]]:
        """Fetch the tokens on the address history, paginated

        Returns the total number of different tokens and a list of tokens found.
        """
        total, tokens = self.db_client.get_address_tokens(address, limit, offset)

        return total, [TokenEntry.from_dict(token) for token in tokens]
