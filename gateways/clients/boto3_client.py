from functools import lru_cache
from typing import Any, Optional

from boto3.session import Session


@lru_cache(maxsize=None)
def get_boto3_client(service: str, endpoint_url: Optional[str]) -> Any:
    """Return the boto3 client for the service and endpoint, built once per process.

    Building a boto3 client is slow and leaves a lot of cyclic garbage behind.
    With a new client on every Lambda invocation, the heap grows until Python
    runs a full garbage collection, which pauses a warm 256 MB Lambda for
    several seconds. Warm invocations reuse this client instead, which also
    keeps the connection pool open between invocations.

    :param service: boto3 service name, e.g. "s3" or "lambda"
    :type service: str
    :param endpoint_url: custom endpoint, or None for the AWS default
    :type endpoint_url: Optional[str]
    """
    return Session().client(service, endpoint_url=endpoint_url)
