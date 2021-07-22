from freezegun import freeze_time
from domain.network.network import uptime_to_up_since, AggregatedPeer, AggregatedNode, Network
from tests.fixtures.node_factory import NodeFactory, PeerFactory
from tests.fixtures.network_factory import AggregatedPeerFactory, AggregatedNodeFactory, NetworkFactory


class TestNetwork:

    @freeze_time('2020-08-28 10:30:00')
    def test_uptime_to_since(self):
        uptime = 1000
        result = uptime_to_up_since(uptime)

        assert result == 1598609600

    def test_aggregated_peer_from_peer(self):
        peer = PeerFactory()
        aggregated_peer = AggregatedPeer.from_peer(peer)

        assert aggregated_peer.id == peer.id
        assert aggregated_peer.app_version == peer.app_version
        assert aggregated_peer.entrypoints == peer.entrypoints
        assert aggregated_peer.warning_flags == peer.warning_flags

    def test_aggregated_peer_to_dict(self):
        aggregated_peer = AggregatedPeerFactory()

        agp_dict = aggregated_peer.to_dict()

        assert agp_dict['id'] == aggregated_peer.id
        assert agp_dict['address'] == aggregated_peer.address
        assert agp_dict['connected_to'] == set()

    def test_aggregated_peer_add_connected_to(self):
        aggregated_peer = AggregatedPeerFactory()

        assert aggregated_peer.connected_to == set()

        aggregated_peer.add_connected_to('abcde123')

        assert aggregated_peer.connected_to == set(['abcde123'])

    def test_aggregated_node_from_node(self):
        node = NodeFactory()
        aggregated_node = AggregatedNode.from_node(node)

        assert aggregated_node.id == node.id
        assert aggregated_node.entrypoints == node.entrypoints
        assert aggregated_node.connected_peers[0] == node.connected_peers[0].id

    def test_aggregated_node_to_dict(self):
        aggregated_node = AggregatedNodeFactory()

        agn_dict = aggregated_node.to_dict()

        assert agn_dict['id'] == aggregated_node.id
        assert agn_dict['app_version'] == aggregated_node.app_version
        assert agn_dict['connected_peers'] == aggregated_node.connected_peers

    def test_network_to_dict(self):
        network = NetworkFactory()

        network_dict = network.to_dict()

        assert network_dict['nodes'][0]['id'] == network.nodes[0].id
        assert network_dict['peers'][0]['id'] == network.peers[0].id

    def test_network_from_dict(self):
        network = NetworkFactory()
        network_dict = network.to_dict()

        new_network = Network.from_dict(network_dict)

        assert network.nodes[0].id == new_network.nodes[0].id
        assert network.nodes[0].app_version == new_network.nodes[0].app_version

        assert network.peers[0].id == new_network.peers[0].id
        assert network.peers[0].app_version == new_network.peers[0].app_version
