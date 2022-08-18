from typing import List, Optional

from gateways.wallet_service_gateway import WalletServiceGateway


class WalletService:

    def __init__(self, wallet_service_gateway: Optional[WalletServiceGateway] = None) -> None:
        self.wallet_service_gateway = wallet_service_gateway or WalletServiceGateway()

    def address_balance(self, address: str, token: str) -> dict:
        balance = self.wallet_service_gateway.address_balance(address, token)

        return balance.to_dict()

    def address_history(self, address: str, token: str, limit: int, offset: int) -> List[dict]:
        history = self.wallet_service_gateway.address_history(address, token, limit, offset)

        return [tx.to_dict() for tx in history]

    def address_tokens(self, address: str, limit: int, offset: int) -> dict:
        total, tokens = self.wallet_service_gateway.address_tokens(address, limit, offset)
        return {
            'total': total,
            'tokens': {token.token_id: token.to_dict() for token in tokens},
        }
