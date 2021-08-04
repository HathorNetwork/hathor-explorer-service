from dataclasses import asdict, dataclass
from enum import Enum

from dacite import Config, from_dict


class ReportType(str, Enum):
    TOKEN = 'token'
    TRANSACTION = 'transaction'


@dataclass
class Report:
    """Dataclass for reports

    :param type: Type of the report
    :type type: :py:class:`domain.report.report.Report`

    :param id: ID (hash) of reported item
    :type id: str

    :param description: User description of the problem
    :type description: str
    """
    type: ReportType
    id: str
    description: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Report':
        return from_dict(data_class=cls, data=dikt, config=Config(cast=[ReportType]))
