from typing import Optional

from common.errors import ApiError
from gateways.wallet_service_gateway import WalletServiceGateway


class WalletService:
    def __init__(
        self, wallet_service_gateway: Optional[WalletServiceGateway] = None
    ) -> None:
        self.wallet_service_gateway = wallet_service_gateway or WalletServiceGateway()

    def _validate_token(self, token: str) -> None:
        if self.wallet_service_gateway.is_reserved_token(token):
            raise ApiError("invalid_parameters")

    def address_balance(self, address: str, token: str) -> dict:
        self._validate_token(token)
        balance = self.wallet_service_gateway.address_balance(address, token)

        return balance.to_dict()

    def address_history(
        self, address: str, token: str, limit: int, last_tx: Optional[str], last_ts: int
    ) -> dict:
        self._validate_token(token)
        history = self.wallet_service_gateway.address_history(
            address, token, limit, last_tx, last_ts
        )

        return history

    def address_confidential_history(
        self, address: str, limit: int, last_tx: Optional[str], last_ts: int
    ) -> dict:
        return self.wallet_service_gateway.address_confidential_history(
            address, limit, last_tx, last_ts
        )

    def address_tokens(self, address: str, limit: int, offset: int) -> dict:
        total, tokens = self.wallet_service_gateway.address_tokens(
            address, limit, offset
        )
        flags = self.wallet_service_gateway.address_flags(address)
        return {
            "total": total,
            "tokens": {token.token_id: token.to_dict() for token in tokens},
            "has_confidential_activity": flags["has_confidential_activity"],
            "has_hidden_token_activity": flags["has_hidden_token_activity"],
        }
