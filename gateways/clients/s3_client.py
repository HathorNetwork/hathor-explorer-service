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
            # TODO: Add log here
            return None

    def upload_file(self, bucket: str, file: str, content: str) -> dict:
        """Writes a string to a file in the storage.

        :param bucket: bucket name
        :type bucket: str
        :param file: file path
        :type file: str
        :param content: The stringified JSON content
        :type content: str

        :return: the S3 upload metadata
        :rtype: dict
        """
        response = self.client.put_object(
            Body=content.encode(),
            Bucket=bucket,
            Key=file,
            ContentType='application/json'
        )
        return response
