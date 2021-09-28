from domain.node_api.transaction import Transaction
from tests.fixtures.node_api_factory import TransactionFactory


class TestTransaction:

    def assert_input_dict_equal(self, dikt, obj):
        assert dikt['tx_id'] == obj.tx_id
        assert dikt['index'] == obj.index
        assert dikt['data'] == obj.data
        return True

    def assert_output_dict_equal(self, dikt, obj):
        assert dikt['value'] == obj.value
        assert dikt['script'] == obj.script
        return True

    def assert_tx_dict_equal(self, dikt, obj):
        assert dikt['tx_id'] == obj.tx_id
        assert dikt['timestamp'] == obj.timestamp
        assert dikt['version'] == obj.version
        assert dikt['weight'] == obj.weight
        assert sorted(dikt['parents']) == sorted(obj.parents)
        assert len(dikt['inputs']) == len(obj.inputs)
        assert all([
                    self.assert_input_dict_equal(a, b) for a, b in zip(
                        sorted(dikt['inputs'], key=lambda x:x['tx_id']),
                        sorted(obj.inputs, key=lambda x:x.tx_id))
                ])
        assert len(dikt['outputs']) == len(obj.outputs)
        assert all([
                    self.assert_output_dict_equal(a, b) for a, b in zip(
                        sorted(dikt['outputs'], key=lambda x:x['script']),
                        sorted(obj.outputs, key=lambda x:x.script))
                ])
        assert sorted(dikt['tokens']) == sorted(obj.tokens)
        return True

    def test_to_dict(self):
        obj = TransactionFactory()
        obj_dict = obj.to_dict()

        assert obj_dict
        assert self.assert_tx_dict_equal(obj_dict, obj)

    def test_from_dict(self):
        obj = TransactionFactory()
        obj_dict = obj.to_dict()

        new_obj = Transaction.from_dict(obj_dict)

        assert new_obj
        assert new_obj == obj
