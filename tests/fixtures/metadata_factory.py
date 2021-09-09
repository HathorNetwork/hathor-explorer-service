import factory
from faker import Faker

fake = Faker()


def fake_file(type):
    ext = 'pdf' if type.lower() == 'pdf' else None
    domain = fake.domain_name()
    file_path = fake.file_path(category=type.lower(), extension=ext)
    return f"http://{domain}{file_path}"


class TokenNFTMediaFactory(factory.DictFactory):
    type = factory.Faker(
        'random_element',
        elements=['video', 'audio', 'image', 'pdf']
    )
    file = factory.lazy_attribute(lambda o: fake_file(o.type))
    loop = factory.Faker('boolean', chance_of_getting_true=15)
    autoplay = factory.Faker('boolean', chance_of_getting_true=15)


class TokenMetaFactoryBase(factory.DictFactory):
    id = factory.LazyFunction(lambda: f"0000{fake.sha256()}"[:64])
    # id = factory.Faker('sha256')
    verified = factory.Faker('boolean', chance_of_getting_true=10)
    nft = factory.Faker('boolean', chance_of_getting_true=15)
    nft_media = None
    banned = False
    reason = None

    class Params:
        ban = factory.Trait(
            banned=True,
            reason=factory.Faker('sentence'),
        )
        has_media = factory.Trait(
            nft_media=factory.SubFactory(TokenNFTMediaFactory)
        )


class TokenMetadataFactory(TokenMetaFactoryBase):
    ban = factory.Faker('boolean', chance_of_getting_true=15)
    has_media = factory.Faker('boolean', chance_of_getting_true=5)


class TransactionMetadataFactory(factory.DictFactory):
    id = factory.LazyFunction(lambda: f"0000{fake.sha256()}"[:64])
    context = factory.Faker('sentence')
    genesis = factory.Faker('boolean', chance_of_getting_true=10)
