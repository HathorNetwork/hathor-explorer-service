from unittest.mock import MagicMock

from pytest import fixture

from tests.fixtures.report_factory import ReportFactory
from usecases.send_report import SendReport


class TestSendReport:

    @fixture
    def report_gateway(self):
        return MagicMock()

    def test_send(self, report_gateway):
        report = ReportFactory()
        send_report = SendReport()

        report_gateway.send_report = MagicMock(return_value=True)

        send_report = SendReport(report_gateway)

        result = send_report.send(report.type.value, report.id, report.description)

        report_gateway.send_report.assert_called_once()
        assert result

    def test_send_error(self, report_gateway):
        report = ReportFactory()
        report_gateway.send_report = MagicMock(return_value=False)

        send_report = SendReport(report_gateway)

        result = send_report.send(report.type.value, report.id, report.description)

        assert result is False
