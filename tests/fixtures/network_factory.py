from datetime import datetime

from factory import List, lazy_attribute, Factory
from factory.declarations import SubFactory
from faker import Faker

from domain.network.network import AggregatedNode, AggregatedPeer, Network
from domain.network.node import NodeState

fake = Faker()


def entrypoint():
    return f"{fake.ipv4()}:{fake.port_number()}"


class AggregatedPeerFactory(Factory):
    class Meta:
        model = AggregatedPeer

    id = lazy_attribute(lambda o: fake.sha256())
    app_version = lazy_attribute(lambda o: fake.bothify(text='Hathor v0.!#.#'))
    up_since = lazy_attribute(lambda o: datetime.timestamp(fake.date_time_between(start_date='-1y', end_date='-1d')))
    address = lazy_attribute(lambda o: entrypoint())
    state = lazy_attribute(lambda o: fake.random_element(list(NodeState)))
    last_message = lazy_attribute(lambda o: fake.pyfloat(right_digits=14, positive=True, max_value=1))
    latest_timestamp = lazy_attribute(lambda o: fake.pyint(min_value=10_000, max_value=100_000))
    sync_timestamp = lazy_attribute(lambda o: fake.pyint(min_value=10_000, max_value=100_000))
    warning_flags = lazy_attribute(lambda o: fake.random_elements(['no_entrypoints', 'no_peer_id_url'], unique=True))


class AggregatedNodeFactory(Factory):
    class Meta:
        model = AggregatedNode

    id = lazy_attribute(lambda o: fake.sha256())
    app_version = lazy_attribute(lambda o: fake.bothify(text='Hathor v0.!#.#'))
    state = lazy_attribute(lambda o: fake.random_element(list(NodeState)))
    network = lazy_attribute(lambda o: f"testnet-{fake.word()}")
    up_since = lazy_attribute(lambda o: datetime.timestamp(fake.date_time_between(start_date='-1y', end_date='-1d')))
    first_timestamp = lazy_attribute(lambda o: fake.pyint(min_value=10_000, max_value=100_000))
    latest_timestamp = lazy_attribute(lambda o: fake.pyint(min_value=10_000, max_value=100_000))
    entrypoints = lazy_attribute(lambda o: [f"tcp://{entrypoint()}" for i in range(fake.random_int(min=1, max=5))])
    known_peers = lazy_attribute(lambda o: [fake.sha256() for i in range(fake.pyint(min_value=3, max_value=30))])
    connected_peers = List([SubFactory(AggregatedPeerFactory) for i in range(fake.pyint(min_value=3, max_value=15))])


class NetworkFactory(Factory):
    class Meta:
        model = Network

    nodes = List([SubFactory(AggregatedNodeFactory) for i in range(fake.pyint(min_value=3, max_value=7))])
    peers = List([SubFactory(AggregatedPeerFactory) for i in range(fake.pyint(min_value=7, max_value=20))])
