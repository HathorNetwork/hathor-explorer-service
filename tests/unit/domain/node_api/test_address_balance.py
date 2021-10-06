from domain.node_api.address_balance import AddressBalance
from tests.fixtures.node_api_factory import AddressBalanceFactory


class TestAddressBalance:

    def test_to_dict(self):
        obj = AddressBalanceFactory()
        obj_dict = obj.to_dict()

        assert obj_dict
        assert obj_dict['success'] is True
        assert obj_dict['success'] == obj.success
        assert obj_dict['total_transactions'] == obj.total_transactions
        assert sorted(obj_dict['tokens_data']) == sorted(obj.tokens_data)
        assert 'message' not in obj_dict

    def test_from_dict(self):
        obj = AddressBalanceFactory()
        obj_dict = obj.to_dict()

        new_obj = AddressBalance.from_dict(obj_dict)

        assert new_obj
        assert new_obj.success is True
        assert new_obj.success == obj.success
        assert new_obj.total_transactions == obj.total_transactions
        assert sorted(new_obj.tokens_data) == sorted(obj.tokens_data)
        assert new_obj.message is None
        assert new_obj.message == obj.message

    def test_error_to_dict(self):
        obj = AddressBalanceFactory(fail=True)
        obj_dict = obj.to_dict()

        assert obj_dict
        assert obj_dict['success'] is False
        assert obj_dict['success'] == obj.success
        assert obj_dict['message'] == obj.message
        assert obj_dict['total_transactions'] is None
        assert obj_dict['total_transactions'] == obj.total_transactions
        assert obj_dict['tokens_data'] is None
        assert obj_dict['tokens_data'] == obj.tokens_data

    def test_error_from_dict(self):
        obj = AddressBalanceFactory(fail=True)
        obj_dict = obj.to_dict()
        new_obj = AddressBalance.from_dict(obj_dict)

        assert new_obj
        assert new_obj.success == obj.success is False
        assert new_obj.message == obj.message
        assert new_obj.total_transactions is None
        assert new_obj.total_transactions == obj.total_transactions
        assert new_obj.tokens_data is None
        assert new_obj.tokens_data == obj.tokens_data
