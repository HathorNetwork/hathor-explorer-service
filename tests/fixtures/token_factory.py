import re

from factory import Factory, lazy_attribute
from faker import Faker

from domain.tx.token import Token, TokenMetadata, TokenNFT, TokenNFTType

fake = Faker()


def token_symbol(name):
    first_name = name.split(' ')[0]
    symbol = re.sub(r'[aeiou\s]', '', first_name).upper()[:5]
    if len(symbol) < 3:
        symbol = f"{symbol}TK"[:3]

    return symbol


class TokenNFTFactory(Factory):
    class Meta:
        model = TokenNFT

    type = fake.random_element(list(TokenNFTType))
    # Fake file_path does not handle PDF category, then we need to specifically ask for a pdf extension
    if type.value == 'PDF':
        file = lazy_attribute(lambda o: f"http://{fake.domain_name()}{fake.file_path(extension='pdf')}")
    else:
        file = lazy_attribute(lambda o: f"http://{fake.domain_name()}{fake.file_path(category=o.type.value.lower())}")
    loop = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=15))
    autoplay = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=15))


class TokenMetadataFactory(Factory):
    class Meta:
        model = TokenMetadata

    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    verified = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=10))
    banned = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=15))
    reason = lazy_attribute(lambda o: fake.sentence() if o.banned else None)
    nft = lazy_attribute(lambda o: TokenNFTFactory() if fake.boolean(chance_of_getting_true=5) else None)


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
