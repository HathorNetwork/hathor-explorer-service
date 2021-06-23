from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.node_factory import NodeFactory
from usecases.save_node_data import SaveNodeData


class TestSaveNodeData:

    @fixture
    def node_gateway(self):
        return MagicMock()

    def test_save(self, node_gateway):
        node_gateway.save_node = MagicMock(return_value=True)

        node = NodeFactory()
        payload = node.to_dict()

        save_node_data = SaveNodeData(node_gateway)

        result = save_node_data.save(payload)

        assert result
        node_gateway.save_node.assert_called_once_with(node.id, node)
