from dataclasses import dataclass
from typing import List, Optional

from dacite import from_dict

from common.errors import HathorCoreMalformedToken, HathorCoreUnknownToken
from domain.tx.token import Token


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

    def to_token(self, id: str) -> Token:
        if not self.success:
            raise HathorCoreUnknownToken('unknown_token')

        try:
            return Token(
                id=id,
                name=self.name,  # type: ignore
                symbol=self.symbol,  # type: ignore
                total_supply=self.total,  # type: ignore
                transactions_count=self.transactions_count,  # type: ignore
                can_melt=len(self.melt) > 0,  # type: ignore
                can_mint=len(self.mint) > 0  # type: ignore
            )
        except Exception:
            raise HathorCoreMalformedToken('malformed_token')
