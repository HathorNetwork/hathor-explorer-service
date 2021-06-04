from typing import Union

from boto3.session import Session
from common.configuration import S3_ENDPOINT


class S3Client:
    """This is an abstraction for boto3 s3 client
    """
    def __init__(self) -> None:
        session = Session()
        if S3_ENDPOINT is None:
            self.client = session.client('s3')
        else:
            self.client = session.client('s3', endpoint_url=S3_ENDPOINT)

    def load_file(self, bucket: str, file: str) -> Union[str, None]:
        """Loads contents from a file from s3 bucket

        :param bucket: bucket name
        :type bucket: str
        :param file: file path
        :type file: str
        :return: the result body
        :rtype: str
        """
        try:
            response = self.client.get_object(Bucket=bucket, Key=file)
            return response['Body'].read().decode()
        except self.client.exceptions.NoSuchKey:
            return None
