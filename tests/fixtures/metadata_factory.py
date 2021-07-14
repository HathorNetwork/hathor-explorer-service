from factory import Factory, lazy_attribute
from factory.declarations import SubFactory
from faker import Faker

from domain.metadata.metadata import MetadataType
from domain.metadata.token_metadata import TokenMetadata, TokenNFT, MetaToken, TokenNFTType

fake = Faker()


class TokenNFTFactory(Factory):
    class Meta:
        model = TokenNFT

    type = lazy_attribute(lambda o: fake.random_element(list(TokenNFTType)))
    file = lazy_attribute(lambda o: f"http://{fake.domain_name()}{fake.file_path(category=o.type.value.lower())}")


class MetaTokenFactory(Factory):
    class Meta:
        model = MetaToken

    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    verified = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=10))
    banned = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=15))
    reason = lazy_attribute(lambda o: fake.sentence() if o.banned else None)
    nft = lazy_attribute(lambda o: TokenNFTFactory() if fake.boolean(chance_of_getting_true=5) else None)


class TokenMetadataFactory(Factory):
    class Meta:
        model = TokenMetadata

    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    # data = SubFactory(MetaTokenFactory)
