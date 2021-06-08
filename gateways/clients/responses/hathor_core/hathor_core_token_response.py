from dataclasses import dataclass
from typing import List, Optional
from domain.tx.token import Token
from dacite import from_dict


@dataclass
class HathorCoreTokenResponse:

    name: Optional[str]
    success: bool
    message: Optional[str]
    symbol: Optional[str]
    total: Optional[int]
    transactions_count: Optional[int]
    melt: Optional[List[dict]]
    mint: Optional[List[dict]]

    @classmethod
    def from_dict(cls, dikt: dict) -> 'HathorCoreTokenResponse':
        return from_dict(data_class=cls, data=dikt)

    def to_domain(self, id: str) -> Token:
        if not self.success:
            raise Exception('unknown_token')

        return Token(
            id=id,
            name=self.name,
            symbol=self.symbol,
            total_supply=self.total,
            transactions_count=self.transactions_count,
            can_melt=len(self.melt) > 0,
            can_mint=len(self.mint) > 0
        )
