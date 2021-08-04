from factory import Factory, lazy_attribute
from faker import Faker

from domain.report.report import Report, ReportType

fake = Faker()


class ReportFactory(Factory):
    class Meta:
        model = Report

    type = lazy_attribute(lambda o: fake.random_element(list(ReportType)))
    id = lazy_attribute(lambda o: f"0000{fake.sha256()}"[:64])
    description = lazy_attribute(lambda o: fake.sentence())
