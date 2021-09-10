from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.network_factory import NetworkFactory
from usecases.get_network import GetNetwork


class TestGetNetwork:

    @fixture
    def node_gateway(self):
        return MagicMock()

    def test_get(self, node_gateway):
        network = NetworkFactory()

        node_gateway.get_network = MagicMock(return_value=network)

        get_network = GetNetwork(node_gateway)

        result = get_network.get()

        assert result
        assert result['nodes'][0]['id'] == network.nodes[0].id
        assert result['peers'][0]['id'] == network.peers[0].id

    def test_get_not_found(self, node_gateway):
        node_gateway.get_network = MagicMock(return_value=None)

        get_network = GetNetwork(node_gateway)

        result = get_network.get()

        assert result is None
