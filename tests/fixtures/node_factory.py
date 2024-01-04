from factory import Factory, List, lazy_attribute
from factory.declarations import SubFactory
from faker import Faker

from domain.network.node import Node, NodeState, Peer

fake = Faker()


def entrypoint():
    return f"{fake.ipv4()}:{fake.port_number()}"


class PeerFactory(Factory):
    class Meta:
        model = Peer

    id = lazy_attribute(lambda o: fake.sha256())
    app_version = lazy_attribute(lambda o: fake.bothify(text="Hathor v0.!#.#"))
    uptime = lazy_attribute(lambda o: fake.pyfloat(right_digits=11, positive=True))
    address = lazy_attribute(lambda o: entrypoint())
    state = lazy_attribute(lambda o: fake.random_element(list(NodeState)))
    last_message = lazy_attribute(
        lambda o: fake.pyfloat(right_digits=14, positive=True, max_value=1)
    )
    protocol_version = lazy_attribute(
        lambda o: fake.random_element(["sync-v1.1", "sync-v2"])
    )

    @lazy_attribute
    def latest_timestamp(self):
        if self.protocol_version.startswith("sync-v1"):
            return fake.pyint(min_value=10_000, max_value=100_000)
        else:
            return None

    @lazy_attribute
    def sync_timestamp(self):
        if self.protocol_version.startswith("sync-v1"):
            return fake.pyint(min_value=10_000, max_value=self.latest_timestamp)
        else:
            return None

    @lazy_attribute
    def peer_best_block(self):
        if self.protocol_version.startswith("sync-v2"):
            return {
                "height": fake.pyint(1_000_000, 5_000_000),
                "id": fake.sha256(),
            }
        else:
            return None

    @lazy_attribute
    def synced_block(self):
        if self.protocol_version.startswith("sync-v2"):
            return {
                "height": fake.pyint(1_000_000, self.peer_best_block["height"]),
                "id": fake.sha256(),
            }
        else:
            return None

    warning_flags = lazy_attribute(
        lambda o: fake.random_elements(
            ["no_entrypoints", "no_peer_id_url"], unique=True
        )
    )
    entrypoints = lazy_attribute(
        lambda o: []
        if "no_entrypoints" in o.warning_flags
        else [f"tcp://{entrypoint()}"]
    )


class NodeFactory(Factory):
    class Meta:
        model = Node

    id = lazy_attribute(lambda o: fake.sha256())
    app_version = lazy_attribute(lambda o: fake.bothify(text="Hathor v0.!#.#"))
    state = lazy_attribute(lambda o: fake.random_element(list(NodeState)))
    network = lazy_attribute(lambda o: f"testnet-{fake.word()}")
    uptime = lazy_attribute(lambda o: fake.pyfloat(right_digits=11, positive=True))
    first_timestamp = lazy_attribute(
        lambda o: fake.pyint(min_value=10_000, max_value=100_000)
    )
    latest_timestamp = lazy_attribute(
        lambda o: fake.pyint(min_value=10_000, max_value=100_000)
    )
    entrypoints = lazy_attribute(
        lambda o: [
            f"tcp://{entrypoint()}" for i in range(fake.random_int(min=1, max=5))
        ]
    )
    known_peers = lazy_attribute(
        lambda o: [fake.sha256() for i in range(fake.pyint(min_value=3, max_value=30))]
    )
    connected_peers = List(
        [SubFactory(PeerFactory) for i in range(fake.pyint(min_value=3, max_value=15))]
    )
