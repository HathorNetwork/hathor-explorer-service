import re

from factory import Factory, lazy_attribute
from faker import Faker

from domain.tx.token import Token

fake = Faker()


def token_symbol(name):
    first_name = name.split(' ')[0]
    symbol = re.sub(r'[aeiou\s]', '', first_name).upper()[:5]
    if len(symbol) < 3:
        symbol = f"{symbol}TK"[:3]

    return symbol


class TokenFactory(Factory):
    class Meta:
        model = Token

    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    name = lazy_attribute(lambda o: f"{fake.word().capitalize()} Token")
    symbol = lazy_attribute(lambda o: token_symbol(o.name))
    total_supply = lazy_attribute(lambda o: fake.random_int(min=1, max=999999))
    transactions_count = lazy_attribute(lambda o: fake.random_int(min=1, max=2000))
    can_mint = lazy_attribute(lambda o: fake.boolean())
    can_melt = lazy_attribute(lambda o: fake.boolean())
