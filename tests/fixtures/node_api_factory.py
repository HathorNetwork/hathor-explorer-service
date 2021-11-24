import re

import factory
from faker import Faker

fake = Faker()


class DecodedOutputFactory(factory.DictFactory):
    # tx_id = factory.lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    type = factory.Faker('word')
    address = factory.Faker('pystr')
    timelock = factory.Faker('random_int')


class TxInputFactory(factory.DictFactory):
    # tx_id = factory.lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    tx_id = factory.Faker('sha256')
    index = factory.Faker('random_int')
    script = factory.Faker('pystr')
    token_data = factory.Faker('random_int', max=255)
    token = factory.Faker('sha256')
    value = factory.Faker('random_int')
    decoded = factory.SubFactory(DecodedOutputFactory)


class TxOutputFactory(factory.DictFactory):
    value = factory.Faker('random_int')
    script = factory.Faker('pystr')
    token = factory.Faker('sha256')
    spent_by = factory.Faker('sha256')
    decoded = factory.SubFactory(DecodedOutputFactory)
    token_data = factory.Faker('random_int', max=255)


class TransactionFactory(factory.DictFactory):
    # tx_id = factory.lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    tx_id = factory.Faker('sha256')
    timestamp = factory.Faker('random_int', min=0, max=999999999)
    version = factory.Faker('random_int', min=1, max=2)
    weight = factory.Faker('pyfloat', positive=True)
    parents = factory.List([factory.Faker('sha256')]*2)
    inputs = factory.LazyFunction(lambda: [TxInputFactory() for _ in range(fake.random_int(min=1, max=20))])
    outputs = factory.LazyFunction(lambda: [TxOutputFactory() for _ in range(fake.random_int(min=1, max=20))])


def token_symbol(name):
    first_name = name.split(' ')[0]
    symbol = re.sub(r'[aeiou\s]', '', first_name).upper()[:5]
    if len(symbol) < 3:
        symbol = f"{symbol}TK"[:3]

    return symbol


class AddressBalanceTokenDataFactory(factory.DictFactory):
    name = factory.lazy_attribute(lambda o: f"{fake.word().capitalize()} Token")
    symbol = factory.lazy_attribute(lambda o: token_symbol(o.name))
    received = factory.Faker('random_int', min=1, max=999999)
    spent = factory.lazy_attribute(lambda o: fake.random_int(min=1, max=o.received))


def gen_tokens_data(qty=1):
    tokens = {}
    for i in range(qty):
        tokens[f"0000{fake.sha256()}"[:64]] = AddressBalanceTokenDataFactory()
    return tokens


class AddressBalanceFactory(factory.DictFactory):
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


class AddressSearchFactory(factory.DictFactory):
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


class VersionResourceFactory(factory.DictFactory):
    version = factory.Faker('ipv4')  # not actuallt ipv4, but it generated some dot separated numbers
    network = factory.Faker('word')
    min_weight = factory.Faker('random_int', max=100)
    min_tx_weight = factory.Faker('random_int', max=100)
    min_tx_weight_coefficient = factory.Faker('pyfloat', positive=True)
    token_deposit_percentage = factory.Faker('pyfloat', positive=True, max_value=1)
    min_tx_weight_k = factory.Faker('random_int', max=999)
    reward_spend_min_blocks = factory.Faker('random_int')
    max_number_inputs = factory.Faker('random_int')
    max_number_outputs = factory.Faker('random_int')
