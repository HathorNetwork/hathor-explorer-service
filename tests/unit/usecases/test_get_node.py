from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.node_factory import NodeFactory
from usecases.get_node import GetNode


class TestGetNode:

    @fixture
    def node_gateway(self):
        return MagicMock()

    def test_get(self, node_gateway):
        node = NodeFactory()

        node_gateway.get_node = MagicMock(return_value=node)

        get_node = GetNode(node_gateway)

        result = get_node.get(node.id)

        assert result
        assert result['id'] == node.id

    def test_get_not_found(self, node_gateway):
        node_gateway.get_node = MagicMock(return_value=None)

        get_node = GetNode(node_gateway)

        result = get_node.get('abcdef1234567890')

        assert result is None
