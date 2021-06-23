from unittest.mock import MagicMock

from pytest import fixture

from usecases.list_available_nodes import ListAvailableNodes


class TestListAvailableNodes:

    @fixture
    def node_gateway(self):
        return MagicMock()

    def test_list(self, node_gateway):
        node_gateway.list_node_keys = MagicMock(return_value=['a', 'b', 'c'])

        list_availablke_nodes = ListAvailableNodes(node_gateway)

        result = list_availablke_nodes.list()

        assert result
        assert result == ['a', 'b', 'c']
