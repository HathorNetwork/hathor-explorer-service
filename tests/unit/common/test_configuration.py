from common.configuration import Environment


class TestConfiguration:
    def test_environment_props(self):
        assert Environment.PROD.is_prod is True
        assert Environment.PROD.is_dev is False
        assert Environment.PROD.is_test is False
        assert Environment.DEV.is_prod is False
        assert Environment.DEV.is_dev is True
        assert Environment.DEV.is_test is False
        assert Environment.TEST.is_prod is False
        assert Environment.TEST.is_dev is False
        assert Environment.TEST.is_test is True
        assert Environment.default() is Environment.DEV
