from unittest.mock import MagicMock

from pytest import fixture
from deepdiff import DeepDiff

from domain.network.network import Network
from tests.fixtures.network_factory import NetworkFactory
from usecases.aggregate_node_data import AggregateNodeData, EarlyStopDiff


class TestEarlyStopDiff:

    def test_multiple_diffs(self):
        data11 = {'a': 1, 'b': 2}
        data12 = {'a': 3, 'b': 4}
        diff1 = DeepDiff(data11, data12, custom_operators=[EarlyStopDiff()])
        # On the diff tree each key represents a type of modification (e.g. values_changed, dictionary_item_removed)
        # Each value is a list of differences of this type
        # Assert having 1 difference in all types (when we have more than 1) means we stopped when we found the first
        print(diff1)
        assert sum(len(v) for v in diff1.tree.values()) == 1

        data21 = {'a': 1, 'b': 1}
        data22 = {'b': 2, 'c': 1, 'd': 1}
        diff2 = DeepDiff(data21, data22, custom_operators=[EarlyStopDiff()])
        # The only instance where we would have more than 1 difference is when we remove or add a key
        # Then it's 1 for each removed or added key, ignoring changes on values
        print(diff2)
        assert sum(len(v) for v in diff2.tree.values()) == 3

        data31 = {'foo': {'a': 1, 'b': 2}, 'foz': {'some': 'thing'}}
        data32 = {'foo': {'a': 2, 'b': 2}, 'foz': {'to': 'change'}}
        diff3 = DeepDiff(data31, data32, custom_operators=[EarlyStopDiff()])
        # DFS on ordered keys means we wont check 'foz' since we found a diff on a subkey of 'foo'
        print(diff3)
        assert sum(len(v) for v in diff3.tree.values()) == 1

        data41 = {'foo': {'a': 1, 'b': 2}, 'foz': {'some': 'thing'}}
        data42 = {'foo': {'a': 1, 'b': 2}, 'foz': {'to': 'change'}}
        diff4 = DeepDiff(data41, data42, custom_operators=[EarlyStopDiff()])
        # It also means we will check on 'foz' if we dont find diffs on 'foo'
        print(diff4)
        assert sum(len(v) for v in diff4.tree.values()) == 2



class TestAggregateNodeData:

    @fixture
    def node_gateway(self):
        return MagicMock()

    def test_aggregate_no_diff(self, node_gateway):
        network = NetworkFactory()
        network2 = Network.from_dict(network.to_dict())

        for i in range(len(network2.nodes)):
            network2.nodes[i].uptime += 1

        for i in range(len(network2.peers)):
            network2.peers[i].uptime += 1

        node_gateway.aggregate_network = MagicMock(return_value=network2)
        node_gateway.get_network = MagicMock(return_value=network)
        node_gateway.save_network = MagicMock()

        aggregate_node_data = AggregateNodeData(node_gateway=node_gateway)

        result = aggregate_node_data.aggregate()

        node_gateway.save_network.assert_not_called()
        assert result

    def test_aggregate_no_old_network(self, node_gateway):
        network = NetworkFactory()
        node_gateway.aggregate_network = MagicMock(return_value=network)
        node_gateway.get_network = MagicMock(return_value=None)
        node_gateway.save_network = MagicMock(return_value=True)

        aggregate_node_data = AggregateNodeData(node_gateway=node_gateway)

        result = aggregate_node_data.aggregate()

        node_gateway.save_network.assert_called_once_with(network)
        assert result

    def test_aggregate_and_save(self, node_gateway):
        network = NetworkFactory()
        network2 = NetworkFactory()
        node_gateway.aggregate_network = MagicMock(return_value=network)
        node_gateway.get_network = MagicMock(return_value=network2)
        node_gateway.save_network = MagicMock()

        aggregate_node_data = AggregateNodeData(node_gateway=node_gateway)

        result = aggregate_node_data.aggregate()

        node_gateway.save_network.assert_called_once_with(network)
        assert result
