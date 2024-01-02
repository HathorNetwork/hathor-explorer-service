from domain.network.node import Node, NodeState
from tests.fixtures.hathor_core_fixtures import (
    HATHOR_CORE_MAINNET_GET_STATUS,
    HATHOR_CORE_TESTNET_GET_STATUS,
)
from tests.fixtures.node_factory import NodeFactory


class TestNode:
    def test_to_dict(self):
        node = NodeFactory()

        node_dict = node.to_dict()

        assert node_dict
        assert node_dict["id"] == node.id
        assert node_dict["state"] in list(NodeState)
        assert node_dict["entrypoints"][0] == node.entrypoints[0]
        assert node_dict["connected_peers"][0]["id"] == node.connected_peers[0].id

    def test_from_dict(self):
        node = NodeFactory()

        node_dict = node.to_dict()

        new_node = Node.from_dict(node_dict)

        assert new_node
        assert new_node.id == node.id
        assert new_node.state == node.state
        assert new_node.entrypoints == node.entrypoints
        assert new_node.connected_peers[0].id == node.connected_peers[0].id

    def test_from_status_dict(self):
        mainnet = Node.from_status_dict(HATHOR_CORE_MAINNET_GET_STATUS)

        assert mainnet
        assert (
            mainnet.id
            == "f0e156e9bea669724ce5d37bbf67e997e0cf04d067a3d0400aad8f746387401e"
        )
        assert mainnet.state == NodeState("READY")
        assert mainnet.entrypoints[0] == "tcp://18.196.44.159:40403"
        assert (
            mainnet.connected_peers[0].id
            == "1ba45f948775d5276947fd6bcde1f512cd5761038a5f334ca2b2ac4cb75b17d6"
        )
        assert mainnet.connected_peers[0].latest_timestamp == 1704224442
        assert mainnet.connected_peers[0].entrypoints == []
        assert (
            mainnet.connected_peers[2].id
            == "e6dc285d498cf1f2c24185808334bf5ddb67d54f8fc67f90d7c927e7040cfbe3"
        )
        assert mainnet.connected_peers[2].peer_best_block.height == 4125507
        assert mainnet.connected_peers[2].entrypoints == ["tcp://3.73.101.11:40403"]

        testnet = Node.from_status_dict(HATHOR_CORE_TESTNET_GET_STATUS)

        assert testnet
        assert (
            testnet.id
            == "4d72a3de11b709db29a4fcea5e0e9d7d646582c6bc43eb5fc31dc13e7f2c21b9"
        )
        assert testnet.state == NodeState("READY")
        assert testnet.entrypoints[0] == "tcp://18.197.75.137:40403"
        assert (
            testnet.connected_peers[0].id
            == "ef1e6f7b80d51baedac0e8a4be2eb603d18f3b818b75d37b2753c999dc4a3bb0"
        )
        assert testnet.connected_peers[0].peer_best_block.height == 3454218
        assert testnet.connected_peers[0].entrypoints == ["tcp://3.67.174.108:40403"]
