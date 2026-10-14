import json
from functools import lru_cache
from typing import Any, Optional

import boto3

from common.configuration import LAMBDA_INVOKE_URL


@lru_cache(maxsize=None)
def get_boto3_lambda_client(endpoint_url: Optional[str]) -> Any:
    """Return the boto3 lambda client for the endpoint, built once per process.

    See `gateways.clients.s3_client.get_boto3_s3_client` for why the client
    is reused instead of built on every call.

    :param endpoint_url: custom endpoint, or None for the AWS default
    :type endpoint_url: Optional[str]
    """
    return boto3.session.Session().client("lambda", endpoint_url=endpoint_url)


class LambdaClient:
    """This is an abstraction for boto3 lambda client"""

    def __init__(self) -> None:
        self.client = get_boto3_lambda_client(LAMBDA_INVOKE_URL)

    def invoke_async(self, function: str, payload: dict) -> int:
        """Invoke lambda asyncronously

        :param function: Name of function do be invoked
        :type function: str

        :param payload: Body of the request
        :type payload: dict

        :return: Request status code
        :rtype: int
        """
        return self.client.invoke(
            InvocationType="Event", FunctionName=function, Payload=json.dumps(payload)
        )["StatusCode"]

    def invoke(self, function: str, payload: dict) -> dict:
        """Invoke lambda syncronously

        Response structure
        {
            'StatusCode': 123,
            'FunctionError': 'string',
            'LogResult': 'string',
            'Payload': StreamingBody(),
            'ExecutedVersion': 'string'
        }

        :param function: Name of function do be invoked
        :type function: str

        :param payload: Body of the request
        :type payload: dict

        :return: Request response
        :rtype: dict
        """
        return self.client.invoke(FunctionName=function, Payload=json.dumps(payload))
