import pytest

from gateways.clients.lambda_client import get_boto3_lambda_client
from gateways.clients.s3_client import get_boto3_s3_client


@pytest.fixture(autouse=True)
def clear_boto3_client_caches():
    """The boto3 clients are cached per process, so a Stubber activated in one
    test would stay attached to the client in the next. Start every test clean."""
    get_boto3_s3_client.cache_clear()
    get_boto3_lambda_client.cache_clear()
    yield
    get_boto3_s3_client.cache_clear()
    get_boto3_lambda_client.cache_clear()
