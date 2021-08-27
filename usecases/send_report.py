from typing import Optional

from domain.report.report import Report
from gateways.report_gateway import ReportGateway


class SendReport:

    def __init__(self, report_gateway: Optional[ReportGateway] = None) -> None:
        self.report_gateway = report_gateway or ReportGateway()

    def send(self, type: Optional[str], id: Optional[str], description: Optional[str]) -> bool:
        """Build Report object and send

        :param type: type of the report i.e.: 'token'
        :type type: Optional[str]
        :param id: ID of the token or transaction
        :type id: Optional[str]
        :param description: problem described by the user
        :type description: Optional[str]
        :return: if it was succefull sent or not
        :rtype: bool
        """
        report = Report.from_dict({
            'type': type,
            'id': id,
            'description': description
        })

        return self.report_gateway.send_report(report)
