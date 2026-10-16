import pytest

from gateways.clients.boto3_client import get_boto3_client


@pytest.fixture(autouse=True)
def clear_boto3_client_cache():
    """The boto3 clients are cached per process, so a Stubber activated in one
    test would stay attached to the client in the next. Start every test clean."""
    get_boto3_client.cache_clear()
    yield
    get_boto3_client.cache_clear()
