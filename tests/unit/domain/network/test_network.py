from domain.network.network import Network, NodeState
from tests.fixtures.hathor_core_fixtures import HATHOR_CORE_MAINNET_GET_STATUS, HATHOR_CORE_TESTNET_GET_STATUS
from tests.fixtures.network_factory import NetworkFactory


class TestNetowrk:

    def test_to_dict(self):
        network = NetworkFactory()

        network_dict = network.to_dict()

        assert network_dict
        assert network_dict['id'] == network.id
        assert network_dict['state'] in list(NodeState)
        assert network_dict['entrypoints'][0] == network.entrypoints[0]
        assert network_dict['connected_peers'][0]['id'] == network.connected_peers[0].id

    def test_from_dict(self):
        network = NetworkFactory()

        network_dict = network.to_dict()

        new_network = Network.from_dict(network_dict)

        assert new_network
        assert new_network.id == network.id
        assert new_network.state == network.state
        assert new_network.entrypoints == network.entrypoints
        assert new_network.connected_peers[0].id == network.connected_peers[0].id

    def test_from_status_dict(self):
        mainnet = Network.from_status_dict(HATHOR_CORE_MAINNET_GET_STATUS)

        assert mainnet
        assert mainnet.id == '847b9f9979514e33b8713c8d63f0c0cc0ccba9aff067d62a4679f20439595631'
        assert mainnet.state == NodeState('READY')
        assert mainnet.entrypoints[0] == 'tcp://34.218.233.215:40403'
        assert mainnet.connected_peers[0].id == '49c9cdeddc8a5ee94c177628686aba07bca53c481819c921ff16cdd39614bc1c'
        assert mainnet.connected_peers[0].latest_timestamp == 1622151490

        testnet = Network.from_status_dict(HATHOR_CORE_TESTNET_GET_STATUS)

        assert testnet
        assert testnet.id == '4277ccbd10c5b3aec608e5cc8888d612ff275d8645d1069cef24178c5619d17a'
        assert testnet.state == NodeState('READY')
        assert testnet.entrypoints[0] == 'tcp://3.21.242.244:40403'
        assert testnet.connected_peers[0].id == '71df2e6c0927491eb439c68d45b3690d22e4c15beaa174e2487a117c46abd944'
        assert testnet.connected_peers[0].latest_timestamp == 1622140105
