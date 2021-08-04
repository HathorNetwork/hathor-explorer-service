from dataclasses import asdict, dataclass
from enum import Enum
from dacite import from_dict, Config


class ReportType(str, Enum):
    TOKEN = 'token'
    TRANSACTION = 'transaction'


@dataclass
class Report:

    type: ReportType
    id: str
    description: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, dikt: dict) -> 'Report':
        return from_dict(data_class=cls, data=dikt, config=Config(cast=[ReportType]))
