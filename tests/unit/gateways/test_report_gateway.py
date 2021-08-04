from unittest.mock import MagicMock

from pytest import fixture

from gateways.report_gateway import ReportGateway
from tests.fixtures.report_factory import ReportFactory


class TestReportGateway:

    @fixture
    def report_client(self):
        return MagicMock()

    def test_send_report(self, report_client):
        report = ReportFactory()

        report_client.send = MagicMock(return_value=True)

        gateway = ReportGateway(report_client=report_client)

        result = gateway.send_report(report)

        report_client.send.assert_called_once()
        assert result
