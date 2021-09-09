import json
from io import BytesIO
from unittest.mock import patch

from botocore.response import StreamingBody
from botocore.stub import Stubber

from gateways.clients.s3_client import S3Client
from tests.fixtures.metadata_factory import TokenMetadataFactory


class TestS3Client:

    @patch('gateways.clients.s3_client.S3_ENDPOINT', 'http://lambda.invoke.endpoint')
    def test_load_file(self):
        s3_client = S3Client()

        stubber = Stubber(s3_client.client)

        s3_expected_params = {
            'Bucket': 'head',
            'Key': 'c-minor'
        }

        file = json.dumps(TokenMetadataFactory())
        s3_response = {
            'Body': StreamingBody(BytesIO(file.encode()), len(file))
        }
        stubber.add_response('get_object', s3_response, s3_expected_params)
        stubber.activate()

        result = s3_client.load_file('head', 'c-minor')

        assert result == file

    @patch('gateways.clients.s3_client.S3_ENDPOINT', None)
    def test_load_file_error(self):
        s3_client = S3Client()

        stubber = Stubber(s3_client.client)

        s3_expected_params = {
            'Bucket': 'kicked',
            'Key': 'broken'
        }

        stubber.add_client_error('get_object', 'NoSuchKey', expected_params=s3_expected_params)
        stubber.activate()

        result = s3_client.load_file('kicked', 'broken')

        assert result is None
