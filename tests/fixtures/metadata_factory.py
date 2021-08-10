from factory import Factory, lazy_attribute
from factory.declarations import SubFactory
from faker import Faker

from domain.metadata.token_metadata import MetaToken, TokenMetadata, TokenNFTMedia, TokenNFTMediaType
from domain.metadata.transaction_metadata import MetaTransaction, TransactionMetadata

fake = Faker()


class TokenNFTMediaFactory(Factory):
    class Meta:
        model = TokenNFTMedia

    type = lazy_attribute(lambda o: fake.random_element(list(TokenNFTMediaType)))
    file = lazy_attribute(lambda o: f"http://{fake.domain_name()}{fake.file_path(category=o.type.value.lower())}")
    loop = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=15))


class MetaTokenFactory(Factory):
    class Meta:
        model = MetaToken

    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    verified = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=10))
    banned = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=15))
    reason = lazy_attribute(lambda o: fake.sentence() if o.banned else None)
    nft = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=15))
    nft_media = lazy_attribute(lambda o: TokenNFTMediaFactory() if fake.boolean(chance_of_getting_true=5) else None)


class TokenMetadataFactory(Factory):
    class Meta:
        model = TokenMetadata

    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    data = SubFactory(MetaTokenFactory)


class MetaTransactionFactory(Factory):
    class Meta:
        model = MetaTransaction

    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    context = lazy_attribute(lambda o: fake.sentence())
    genesis = lazy_attribute(lambda o: fake.boolean(chance_of_getting_true=10))


class TransactionMetadataFactory(Factory):
    class Meta:
        model = TransactionMetadata

    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    data = SubFactory(MetaTransactionFactory)