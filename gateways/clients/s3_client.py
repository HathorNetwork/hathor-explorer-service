from functools import lru_cache
from typing import Any, Optional, Union

from boto3.session import Session

from common.configuration import S3_ENDPOINT


@lru_cache(maxsize=None)
def get_boto3_s3_client(endpoint_url: Optional[str]) -> Any:
    """Return the boto3 s3 client for the endpoint, built once per process.

    Building a boto3 client is slow and leaves a lot of cyclic garbage behind.
    With a new client on every Lambda invocation, the heap grows until Python
    runs a full garbage collection, which pauses a warm 256 MB Lambda for
    several seconds. Warm invocations reuse this client instead, which also
    keeps the connection pool to S3 open between invocations.

    :param endpoint_url: custom endpoint, or None for the AWS default
    :type endpoint_url: Optional[str]
    """
    return Session().client("s3", endpoint_url=endpoint_url)


class S3Client:
    """This is an abstraction for boto3 s3 client"""

    def __init__(self) -> None:
        self.client = get_boto3_s3_client(S3_ENDPOINT)

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
            return response["Body"].read().decode()
        except self.client.exceptions.NoSuchKey:
            # TODO: Add log here
            return None

    def load_file_bytes(self, bucket: str, file: str) -> Union[bytes, None]:
        """Loads raw bytes from a file in s3 bucket (for binary files such as images)

        :param bucket: bucket name
        :type bucket: str
        :param file: file path
        :type file: str
        :return: the raw file bytes or None if not found
        :rtype: bytes | None
        """
        try:
            response = self.client.get_object(Bucket=bucket, Key=file)
            return response["Body"].read()
        except self.client.exceptions.NoSuchKey:
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
            ContentType="application/json",
        )
        return response
