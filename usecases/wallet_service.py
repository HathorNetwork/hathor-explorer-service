from typing import Optional, List

from gateways.wallet_service_gateway import WalletServiceGateway


class WalletService:

    def __init__(self, wallet_service_gateway: Optional[WalletServiceGateway] = None) -> None:
        self.wallet_service_gateway = wallet_service_gateway or WalletServiceGateway()

    def address_balance(self, address: str, token: str) -> Optional[dict]:
        balance = self.wallet_service_gateway.address_balance(address, token)

        if balance is not None:
            return balance.to_dict()

        return None

    def address_history(self, address: str, token: str, limit: int, skip: int) -> List[dict]:
        history = self.wallet_service_gateway.address_history(address, token, limit, skip)

        return [tx.to_dict() for tx in history]

    def address_tokens(self, address: str) -> List[dict]:
        tokens = self.wallet_service_gateway.address_tokens(address)

        return [token.to_dict() for token in tokens]
