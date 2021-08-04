from typing import Optional

from domain.report.report import Report
from gateways.clients.report_client import ReportClient


class ReportGateway:

    def __init__(self, report_client: Optional[ReportClient] = None) -> None:
        self.report_client = report_client or ReportClient()

    def send_report(self, report: Report) -> bool:
        """Build and send report

        :param report_client: populated Report dataclass, defaults to None
        :type report_client: Optional[:py:class:`gateways.clients.report_client.ReportClient`], optional
        """
        message = f"""
            Type: {report.type}
            ID: {report.id}
            Description: {report.description}
        """
        return self.report_client.send(message)
