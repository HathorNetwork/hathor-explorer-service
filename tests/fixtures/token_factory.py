import factory
from factory import lazy_attribute
from faker import Faker

from domain.tx.token import TokenMetadata, TokenNFT, TokenNFTType

fake = Faker()


class TokenNFTFactory(factory.Factory):
    class Meta:
        model = TokenNFT

    type = lazy_attribute(lambda o: fake.random_element(list(TokenNFTType)))
    file = lazy_attribute(lambda o: f"http://{fake.domain_name()}{fake.file_path(category=o.type.value.lower())}")


class TokenMetadataFactory(factory.Factory):
    class Meta:
        model = TokenMetadata

    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    verified = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=10))
    banned = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=15))
    reason = lazy_attribute(lambda o: fake.sentence() if o.banned else None)
    nft = lazy_attribute(lambda o: TokenNFTFactory() if fake.boolean(chance_of_getting_true=5) else None)
