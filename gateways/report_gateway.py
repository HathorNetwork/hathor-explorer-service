from domain.report.report import Report
from typing import Optional
from gateways.clients.report_client import ReportClient


class ReportGateway:

    def __init__(self, report_client: Optional[ReportClient] = None) -> None:
        self.report_client = report_client or ReportClient()

    def send_report(self, report: Report) -> bool:
        message = f"""
            Type: {report.type}
            ID: {report.id}
            Description: {report.description}
        """
        return self.report_client.send(message)
