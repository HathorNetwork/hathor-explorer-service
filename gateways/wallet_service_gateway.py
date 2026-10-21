from typing import List, Optional, Tuple

from domain.wallet_service import TokenBalance, TokenEntry, TxHistoryEntry
from gateways.clients.wallet_service_db_client import (
    FULLY_SHIELDED_TOKEN_ID,
    WalletServiceDBClient,
)


class WalletServiceGateway:
    def __init__(self, db_client: Optional[WalletServiceDBClient] = None):
        self.db_client = db_client or WalletServiceDBClient()

    def is_reserved_token(self, token: str) -> bool:
        """Whether `token` is an internal token_id that is not a real token."""
        return token == FULLY_SHIELDED_TOKEN_ID

    def address_balance(self, address: str, token: str) -> TokenBalance:
        """Fetch the balance of a token on a particular address."""
        balance = self.db_client.get_address_balance(address, token)
        return TokenBalance.from_dict(balance)

    def address_history(
        self, address: str, token: str, limit: int, last_tx: Optional[str], last_ts: int
    ) -> dict:
        """Fetch the tx history for an address/token pair, paginated."""
        has_next, history = self.db_client.get_address_history(
            address, token, limit, last_tx, last_ts
        )

        tx_history = [TxHistoryEntry.from_dict(tx) for tx in history]

        return {
            "has_next": has_next,
            "history": [tx.to_dict() for tx in tx_history],
        }

    def address_confidential_history(
        self, address: str, limit: int, last_tx: Optional[str], last_ts: int
    ) -> dict:
        """Fetch the txs where the address has FullyShielded involvement, paginated.

        Their token and amount are hidden, so every entry has `token_id` and
        `balance` set to None.
        """
        has_next, history = self.db_client.get_address_history(
            address, FULLY_SHIELDED_TOKEN_ID, limit, last_tx, last_ts
        )

        tx_history = [
            TxHistoryEntry.from_dict({**tx, "token_id": None, "balance": None})
            for tx in history
        ]

        return {
            "has_next": has_next,
            "history": [tx.to_dict() for tx in tx_history],
        }

    def address_tokens(
        self, address: str, limit: int, offset: int
    ) -> Tuple[int, List[TokenEntry]]:
        """Fetch the tokens on the address history, paginated

        Returns the total number of different tokens and a list of tokens found.
        """
        total, tokens = self.db_client.get_address_tokens(address, limit, offset)

        return total, [TokenEntry.from_dict(token) for token in tokens]

    def address_flags(self, address: str) -> dict:
        """Fetch the address's confidential activity flags."""
        return self.db_client.get_address_flags(address)
