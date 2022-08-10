import factory
from faker import Faker

from domain.wallet_service import TokenBalance, TokenEntry, TxHistoryEntry

fake = Faker()


class TokenBalanceFactory(factory.Factory):
    class Meta:
        model = TokenBalance

    token_id = factory.Faker('sha256')
    transactions = factory.Faker('random_int', min=0)
    total_received = factory.Faker('random_int', min=0)
    unlocked_balance = factory.Faker('random_int', min=0)
    locked_balance = factory.Faker('random_int', min=0)
    unlocked_authorities = factory.Faker('random_int', min=0)
    locked_authorities = factory.Faker('random_int', min=0)


class TxHistoryEntryFactory(factory.Factory):
    class Meta:
        model = TxHistoryEntry

    tx_id = factory.Faker('sha256')
    token_id = factory.Faker('sha256')
    timestamp = factory.Faker('random_int', min=0)
    balance = factory.Faker('random_int')
    version = factory.Faker('random_int', min=0, max=3)
    height = factory.Faker('random_int', min=1)


class TokenEntryFactory(factory.Factory):
    class Meta:
        model = TokenEntry

    token_id = factory.Faker('sha256')
    name = factory.Faker('cryptocurrency_name')
    symbol = factory.Faker('cryptocurrency_code')
