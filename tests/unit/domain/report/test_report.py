from dacite.exceptions import WrongTypeError
from pytest import raises

from domain.report.report import Report
from tests.fixtures.report_factory import ReportFactory


class TestReport:

    def test_to_dict(self):
        report = ReportFactory()

        report_dict = report.to_dict()

        assert report_dict
        assert report_dict['id'] == report.id
        assert report_dict['type'] == report.type.value

    def test_from_dict(self):
        report = ReportFactory()
        report_dict = report.to_dict()

        new_report = Report.from_dict(report_dict)

        assert new_report
        assert new_report.id == report_dict['id']
        assert new_report.type.value == report_dict['type']
        assert new_report.description == report_dict['description']

    def test_from_dict_validation(self):
        report_dict = {
            'type': 'token',
            'id': None,
            'description': None
        }

        error_string = r'wrong value type for field "id" - should be "str" instead of value "None" of type "NoneType"'
        with raises(WrongTypeError, match=error_string):
            Report.from_dict(report_dict)
