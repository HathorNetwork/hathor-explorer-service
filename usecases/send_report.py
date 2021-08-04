from typing import Optional
from gateways.report_gateway import ReportGateway
from domain.report.report import Report


class SendReport:

    def __init__(self, report_gateway: Optional[ReportGateway] = None) -> None:
        self.report_gateway = report_gateway or ReportGateway()

    def send(self, type: Optional[str], id: Optional[str], description: Optional[str]) -> bool:
        report = Report.from_dict({
            'type': type,
            'id': id,
            'description': description
        })

        return self.report_gateway.send_report(report)
