import re

import factory
from faker import Faker

from domain.node_api.address_balance import AddressBalance, AddressBalanceTokenData
from domain.node_api.address_search import AddressSearch
from domain.node_api.transaction import Transaction, TxInput, TxOutput

fake = Faker()


class TxInputFactory(factory.Factory):
    class Meta:
        model = TxInput
    # tx_id = factory.lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    tx_id = factory.Faker('sha256')
    index = factory.Faker('random_int')
    data = factory.Faker('pystr')


class TxOutputFactory(factory.Factory):
    class Meta:
        model = TxOutput
    value = factory.Faker('random_int')
    script = factory.Faker('pystr')


class TransactionFactory(factory.Factory):
    class Meta:
        model = Transaction

    # tx_id = factory.lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    tx_id = factory.Faker('sha256')
    timestamp = factory.Faker('random_int', min=0, max=999999999)
    version = factory.Faker('random_int', min=1, max=2)
    weight = factory.Faker('pyfloat', positive=True)
    parents = factory.List([factory.Faker('sha256')]*2)
    inputs = factory.LazyFunction(lambda: [TxInputFactory() for _ in range(fake.random_int(min=1, max=20))])
    outputs = factory.LazyFunction(lambda: [TxOutputFactory() for _ in range(fake.random_int(min=1, max=20))])
    tokens = factory.LazyFunction(lambda: [fake.sha256() for _ in range(fake.random_int(min=1, max=20))])


def token_symbol(name):
    first_name = name.split(' ')[0]
    symbol = re.sub(r'[aeiou\s]', '', first_name).upper()[:5]
    if len(symbol) < 3:
        symbol = f"{symbol}TK"[:3]

    return symbol


class AddressBalanceTokenDataFactory(factory.Factory):
    class Meta:
        model = AddressBalanceTokenData
    name = factory.lazy_attribute(lambda o: f"{fake.word().capitalize()} Token")
    symbol = factory.lazy_attribute(lambda o: token_symbol(o.name))
    received = factory.Faker('random_int', min=1, max=999999)
    spent = factory.lazy_attribute(lambda o: fake.random_int(min=1, max=o.received))


def gen_tokens_data(qty=1):
    tokens = {}
    for i in range(qty):
        tokens[f"0000{fake.sha256()}"[:64]] = AddressBalanceTokenDataFactory()
    return tokens


class AddressBalanceFactory(factory.Factory):
    class Meta:
        model = AddressBalance

    class Params:
        fail = factory.Trait(
            success=False,
            message=factory.Faker('sentence'),
            tokens_data=None,
            total_transactions=None,
        )

    success = True
    tokens_data = factory.lazy_attribute(lambda o: gen_tokens_data(fake.random_int(min=1, max=100)))
    total_transactions = factory.Faker('random_int', min=1, max=999999)
    message = None


class AddressSearchFactory(factory.Factory):
    class Meta:
        model = AddressSearch

    class Params:
        fail = factory.Trait(
            success=False,
            message=factory.Faker('sentence'),
            transactions=None,
            has_more=None,
            total=None,
        )

    success = True
    message = None
    has_more = factory.Faker('boolean')
    total = factory.Faker('random_int', min=1, max=999999)
    transactions = factory.LazyFunction(lambda: [TransactionFactory() for _ in range(fake.random_int(min=1, max=20))])
